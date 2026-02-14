\documentclass[11pt]{article}

\usepackage[a4paper,margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{longtable}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{titlesec}

\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}

\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10}
}

\title{\textbf{ManageBac File Scraper (Fork)}}
\author{Forked from \href{https://github.com/yutotakano/managebac-file-scraper}{yutotakano/managebac-file-scraper}}
\date{License: GNU General Public License v3.0}

\begin{document}

\maketitle

\section*{Overview}

This project is a Python command-line tool that logs into \textbf{ManageBac} and downloads all files from the \textit{Files} tab of your classes. Downloads are organized by class and folder and include retry logic and rate-limit handling.

This fork extends the original archived project with additional functionality and improvements.

\section*{Features}

\begin{itemize}
\item Authenticated login using session cookies
\item Automatic class discovery
\item Recursive folder discovery (BFS crawl)
\item Download all files per class
\item Filter by class name or class ID
\item List folders without downloading
\item Download a specific folder only
\item Retry with exponential backoff
\item Safe filename sanitization
\item Progress indicators with \texttt{tqdm}
\end{itemize}

\section*{Changes in this Fork}

\begin{itemize}
\item Added recursive folder discovery
\item Added \texttt{--class-id} and \texttt{--class-name} filters
\item Added \texttt{--list-folders} mode
\item Added \texttt{--folder-id} selective downloads
\item Improved rate-limit handling and retries
\item Improved filename sanitization
\end{itemize}

\section*{Installation}

\begin{lstlisting}
git clone https://github.com/<your-username>/managebac-file-scraper.git
cd managebac-file-scraper
pip install -r requirements.txt
\end{lstlisting}

\textbf{Requirements:}
Python 3.8+ and the following libraries:
\begin{itemize}
\item requests
\item beautifulsoup4
\item lxml
\item tqdm
\end{itemize}

\section*{Usage}

\begin{lstlisting}
python scrape.py <school_code> <email> <password> <output_dir>
\end{lstlisting}

\subsection*{Arguments}

\begin{longtable}{|p{3cm}|p{10cm}|}
\hline
\textbf{Argument} & \textbf{Description} \\
\hline
school\_code & The part between https:// and .managebac.com \\
email & Your ManageBac login email \\
password & Your ManageBac password \\
output\_dir & Directory where downloads will be saved \\
\hline
\end{longtable}

Each class is saved into its own subfolder.

\section*{Optional Filters}

Download a single class by name:
\begin{lstlisting}
python scrape.py myschool email password downloads --class-name "biology"
\end{lstlisting}

Download a single class by ID:
\begin{lstlisting}
python scrape.py myschool email password downloads --class-id 12345
\end{lstlisting}

List folders without downloading:
\begin{lstlisting}
python scrape.py myschool email password downloads --class-id 12345 --list-folders
\end{lstlisting}

Download a specific folder:
\begin{lstlisting}
python scrape.py myschool email password downloads --class-id 12345 --folder-id 67890
\end{lstlisting}

Show help:
\begin{lstlisting}
python scrape.py -h
\end{lstlisting}

\section*{Security Note}

Avoid putting your password in shell history. Use an environment variable instead:

\begin{lstlisting}
export MB_PASSWORD="your_password"
python scrape.py myschool email $MB_PASSWORD downloads
\end{lstlisting}

Never commit credentials, cookies, or downloaded files.

\section*{Legal Notice}

Use this tool only on accounts and data you are authorized to access.  
You are responsible for complying with your institution’s policies and ManageBac terms of service.

This project is intended for personal backup and educational use.

\section*{Project Status}

This fork is maintained and includes improvements over the original archived repository.

\section*{License}

This project is licensed under the \textbf{GNU General Public License v3.0}.  
It is a fork of the original project by \textbf{yutotakano}, also licensed under GPL-3.0.

See \texttt{LICENSE.md} for the full license text.

\section*{Acknowledgements}

Thanks to \textbf{yutotakano} for the original project.

\end{document}
