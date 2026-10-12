\section{Research Methodology}\label{sec:method}

The primary objective of this study is to investigate whether the widespread adoption of LLM-assisted software development, and more recently of agent-assisted software development, is associated with measurable changes in the diversity and quality of open-source software systems.
Across the three eras of software development discussed in \secref{sec:llmevolution}, i.e., \textit{pre-LLM development}, \textit{potentially LLM-assisted development}, and \textit{detected agentic development}, we formulate the following research questions:

\begin{description} 
    \item[\textbf{RQ1 - Code Diversity:}] To what extent does the code diversity of long-lived open-source software change across eras?
    \begin{description}
        \item[\textbf{RQ1.1} - Semantic Diversity]: we measure the cosine similarity to compare the semantic diversity; lower similarity indicates greater semantic diversity. 
        \item[\textbf{RQ1.2} - Syntactic Diversity]: we measure CodeBLEU score to compare the syntactic diversity; lower similarity indicates greater semantic diversity. 
    \end{description}

    \item[\textbf{RQ2 - Software Quality:}] To what extent does the software quality of long-lived open-source software change across eras considering different quality dimensions?
    \begin{description}
        \item[\textbf{RQ2.1} - Maintainability]: Code Smells, Duplicated Lines, SQALE Index, and Comment Lines. 
        \item[\textbf{RQ2.2} - Complexity]: Cyclomatic and Cognitive Complexity.
        \item[\textbf{RQ2.3} - Reliability]: Bugs
        \item[\textbf{RQ2.4} - Security]: Vulnerabilities and Security Hotspots 
    \end{description}

    \item[\textbf{RQ3 - Structural Characteristics:}] To what extent does the use of LLMs and agentic AIs affect the size and structural characteristics of long-lived open source software?
\end{description}

\subsection{Dataset Curation}

The study uses open-source projects obtained through Software Heritage, with Java and Python as the target languages. 
Projects are intended to be large, popular or actively maintained, and sufficiently long-lived and active to support all three observations. Eventual adoption of coding agents is an intended eligibility criterion, subject to documented evidence. \todo{Insert the total number of selected projects and counts by language; provide the project list, discovery procedure, retrieval date, and source of popularity/activity metadata. Define thresholds and observation windows for size, age, popularity and sustained activity.}
\todo{Document the actual inclusion/exclusion decision for every candidate, with exclusion counts and reasons. Specify handling of forks, mirrors, migrations, monorepositories, archived projects and repositories sharing substantial history.}

\todo{a table describing the project dataset? project counts at discovery + each filtering stage}

\todo{ref to the replication package?}

\paragraph{Evidence of coding-agent adoption}

\todo{Explain how agentic activity was detected~\citep{Robbes2026AgenticMA,robbes2026promises} and hopefully have an indication of "how much" agentic activity was detected per project.}

\paragraph{Software Heritage retrieval.}

\paragraph{Code scope, language composition and coverage.}

\todo{how were the projects assigned one language when multiple were presents.}

\subsection{Analysis Procedure}

In this section, we describe the techniques and tools adopted to analyze and report the data and results to answer our RQs.

\subsubsection{Code Diversity Analysis}
\label{sec:diversity-analysis}
To investigate RQ1, we need to analyze both the semantic (RQ1.1) and syntactic similarity (RQ1.2). First, we extract the functions and create the pairs for both RQs.

\paragraph{Function extraction.}

For each repository snapshot, all functions are extracted using language-specific parsers. Prior to the similarity analysis, a preprocessing step is applied to remove functions that are unlikely to provide meaningful information. Specifically, common boilerplate methods, including getters, setters, and entry-point methods (e.g., \texttt{main}), are excluded using lightweight heuristics based on function names and structural characteristics. A function is excluded if it satisfies any of the following criteria: (i) it contains fewer than two lines of code (LOC), excluding its signature and comments; (ii) it contains fewer than five tokens; or (iii) its name is ``main'' or starts with ``get'' or ``set''. Although these filters may exclude some potentially relevant functions, a substantial number of function pairs were retained for each project (see \secref{sec:evaluation}). 

After this process is completed, we need to isolate the functions that were existing in the first snapshot (pre-LLM)  from those introduced in the second (LLM era) and third (Agentic era). For that, we perform a simple diffing analaysis, were we only keep those functions that were newly added for between each era. Our filtering is based on function signature, where for Java, the class name, method name, parameters names and types are considered. For python the file name, function name, and parameter counts are considered. The reason for this different is the limited parser capability of Python.\lm{continue here}

%\todo{state the actual inclusion filters, minimum length rules etc. With function counts before and after each filter. With a Sankey diagram}

\paragraph{Pair selection.}
\todo{Identify the actual exhaustive, sampled, filtered, or nearest-neighbor comparison policy. Specify budgets or $k$, random seeds, self-pair removal, pair deduplication, orientation, treatment of small projects, and the retained pair count per project/snapshot.}
Given the large number of functions present in the repositories, exhaustively comparing all possible function pairs would result in quadratic complexity, making large-scale analysis computationally infeasible. 

To address this challenge, we adopt a pairing strategy inspired by large-scale code search and clone detection approaches~\citep{}. 
Each function is embedded using a pretrained CodeBERT model. These embeddings are used for candidate retrieval and are indexed using an Approximate Nearest Neighbor (ANN) structure. For each function, the top-(k) nearest neighbors are retrieved based on cosine similarity in the embedding space. This process generates a reduced set of candidate pairs while avoiding the need to enumerate all possible function combinations.

The value of (k) is selected empirically through a validation study. For that, we analyzed a subset of the repositories using exhaustive pairwise comparison to establish a reference set of clone pairs. We then evaluated the candidates retrieval using different values of (k) (e.g., 10, 20, 50, 100), and retrieval effectiveness is measured using Recall@\emph{k}.
The selected value (i.e., 20) corresponds to the smallest (k) achieving a target recall (e.g., at least (95\%)), thereby minimizing computational cost while preserving the vast majority of clone candidates. 
 
 
\paragraph{Syntactic similarity analysis.}

After selecting the functions and creating the pairs,


We perform an analysis to characterize the degree of syntactic similarity between each two functions. 
For this purpose, we employ CodeBLEU~\citep{CodeBLEU}, a source-code similarity metric that combines lexical, syntactic, and semantic matching components. 
CodeBLEU produces a similarity score in the range $[0,1]$, where higher values indicate greater syntactic resemblance. 

As discussed in Section \ref{sec:code-representations}, CodeBLEU is not a purely syntactic measure: its data-flow component incorporates a restricted semantic signal based on dependencies between variables. This component was therefore disabled, putting the emphasis on n-gram and syntax-based components.
 
 \kd{I think we should rename CodeBLEU into CodeBLEU*, as we did for that other paper.}
 
\paragraph{Semantic similarity analysis.}
 
For each candidate function pair \todo{using CodeBERT and CodeT5, that generate vector embedding for each function, capturing its structural and semantic properties.}

Given two functions, $f_1$ and $f_2$, with embeddings $z_1$ and $z_2$, semantic similarity is computed using cosine similarity:

\begin{equation}
\text{sim}(z_1,z_2)=
\frac{z_1 \cdot z_2}
{|z_1||z_2|}.
\end{equation}

\paragraph{Aggregation and longitudinal comparison.}

Each project snapshot produces a distribution of pair-level scores for CodeBERT, CodeT5 and CodeBLEU. 

\todo{aggregation function? what do we report}

\paragraph{Statistical Testing}\lm{TODO: refine this} 
To assess differences in semantic similarity across development eras, we aggregated pair-level similarity scores by computing the median for each project, development era, programming language, and semantic model. This aggregation ensured that projects, rather than individual function pairs, constituted the unit of statistical analysis. We then applied paired Wilcoxon signed-rank tests to compare the three development eras: LLM versus no-LLM, agentic versus no-LLM, and agentic versus LLM. Effect sizes were measured using the rank-biserial correlation. To account for multiple comparisons, $p$-values from all pairwise tests were adjusted using the Benjamini--Hochberg procedure, with a significance level of $\alpha=0.05$.

\subsubsection{Code Quality Metrics}
\label{sec:quality-metrics}

To assess software quality, we adopt a practitioner-oriented measurement strategy based on metrics provided by \textit{SonarQube Community Edition}~\citep{SonarSource2026CloudDocumentation}. 
We use its metrics to characterize quality properties that are directly observable during software development and maintenance~\citep{Yu2023}. 

We distinguish between structural metrics and quality-related metrics. Structural metrics are: \emph{Non-Comment Lines of Code (NCLOC)}, \emph{Functions}, \emph{Classes}, \emph{Files}, and \emph{Statements}. They characterize the size and structure of the software and are analyzed separately as they reflect differences in the amount of implemented functionality rather than changes in software quality.
The quality-related metrics are: \emph{Cyclomatic Complexity}, \emph{Cognitive Complexity}, \emph{Bugs}, \emph{Vulnerabilities}, \emph{Security Hotspots}, \emph{Code Smells}, \emph{Duplicated Lines Density}, \emph{SQALE Index}, \emph{Reliability Rating}, \emph{Security Rating}, and \emph{Comment Lines Density (CLD)}.

For each repository, we compare the three snapshots. This design reduces the influence of repository-specific characteristics, such as domain, architecture, and coding conventions. 
The analysis is performed separately for Java and Python repositories to account for potential language-specific differences in metric distributions and development practices. To simplify interpretation, we adopt a common reporting convention for quality-related metrics: positive changes indicate a greater presence of quality issues (i.e., decreased quality), whereas negative changes indicate a reduction in quality issues (i.e., improved quality).

For metrics for which higher values indicate a greater amount of a quality-related issue, namely Cyclomatic Complexity, Cognitive Complexity, Bugs, Vulnerabilities, Security Hotspots, Code Smells, Duplicated Lines Density, and SQALE Index, we compute the within-repository change as:

\todo{update this for the 3 snapshot design}

\begin{equation}
\Delta Q_{p,m} =
m_{p}^{\mathrm{agentic}} -
m_{p}^{\mathrm{non-agentic}},
\end{equation}

where $p$ denotes a repository and $m$ denotes a quality-related metric. Reliability Rating and Security Rating are treated as ordinal indicators using their numerical encoding, where larger values correspond to poorer ratings, and are therefore interpreted using the same direction convention. Structural metrics, including NCLOC, Number of Functions, Number of Classes, Number of Files, and Number of Statements, are analyzed descriptively as indicators of software size and structure. CLD is likewise treated as a descriptive metric rather than assigned a quality direction.

Because llm and agentic development may change software size, absolute changes in count-based quality metrics may partly reflect the production of additional code. We therefore perform a complementary size-adjusted analysis for Cyclomatic Complexity, Cognitive Complexity, Bugs, Code Smells, Vulnerabilities, Security Hotspots, and SQALE Index by normalizing each metric by the number of functions:

\begin{equation}
m_{\mathrm{density}} =
\frac{m}{\#Functions}.
\end{equation}

For each function-normalized metric, we compute the corresponding within-repository change:

\todo{update this for the 3 snapshot design}

\begin{equation}
\Delta m_{\mathrm{density},p} =
m_{\mathrm{density},p}^{\mathrm{agentic}} -
m_{\mathrm{density},p}^{\mathrm{non-agentic}}.
\end{equation}

Metrics already expressed as densities, namely Duplicated Lines Density and CLD, are not further normalized, while Reliability Rating and Security Rating remain separate ordinal indicators. As a complementary structural measure, we also compute the number of non-comment lines of code per function, $\mathrm{NCLOC}/\#Functions$, to characterize changes in the amount of code associated with each function. This measure is interpreted descriptively rather than as a direct quality indicator.

We additionally report relative changes as a complementary descriptive measure:

\begin{equation}
\Delta m_{\%,p} =
\frac{
m_{p}^{\mathrm{agentic}} -
m_{p}^{\mathrm{non-agentic}}
}{
m_{p}^{\mathrm{non-agentic}}
}
\times 100.
\end{equation}

Absolute differences constitute the primary measure of change, while percentage changes are reported as a complementary descriptive measure to facilitate comparison across metrics with different scales.

To assess whether changes are systematic across repositories, we apply the Wilcoxon signed-rank test to the paired observations for each quality metric, separately for Java and Python. We report the median values, within-repository differences, Benjamini--Hochberg-adjusted $p$-values, and rank-biserial correlations as an effect-size measure. 


Lastly, to organize these measurements from a higher-level perspective, we follow the quality dimensions identified by the systematic mapping study of software metrics by Nunes et al.~\citep{NunesVarela2017}. Cyclomatic Complexity and Cognitive Complexity characterize the \emph{Complexity} dimension; Code Smells, Duplicated Lines Density, SQALE Index, and CLD provide indicators related to \emph{Maintainability}; Bugs and Reliability Rating capture \emph{Reliability}; and Vulnerabilities, Security Hotspots, and Security Rating capture \emph{Security}. We use these dimensions as an organizational framework for summarizing and reporting the individual metric results.


\paragraph{Statistical Testing}\lm{TODO: refine this}
To account for the repeated measurements of the same projects across the three historical generations, we fitted linear mixed-effects models with project as a random intercept and generation, programming language, and their interaction as fixed effects. The dependent variables were continuous density measures derived from software-quality and structural metrics, which were log-transformed using $\log(1+x)$ to reduce skewness and stabilize variance. Planned pairwise contrasts between generations (V1--V2, V2--V3, and V1--V3) were evaluated using the mixed-effects models, while paired Wilcoxon signed-rank tests on the original density values were additionally performed as a non-parametric robustness check; $p$-values were adjusted using the Benjamini--Hochberg procedure to control the false discovery rate (FDR).