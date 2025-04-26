Methods

All automated computations were managed by a Python 3.11 controller script. Each computational step was encapsulated as a discrete agent function, clearly defined by its prompt, model choice, and structured inputs and outputs. Model inferences were executed using Microsoft Azure OpenAI via UCSF Versa, a secure platform employing stateless endpoints that neither retain nor utilize user data for training purposes.

Source Acquisition and Preprocessing
The dataset comprised two independent sources: an audio recording of Dr. Marilu Gorno-Tempini's seminar and a PDF of Dr. Boon Lead Tee’s presentation slides. The audio stream was transcribed verbatim using Whisper-3-large, configured specifically for 16 kHz mono audio input. Slides from the PDF were converted into 300 dpi PNG images using a custom preprocessing utility. These images were subsequently processed by GPT-4o-2024-08-06, utilizing a tailored slide-captioning prompt to generate full-sentence descriptions that preserved technical terminology. Captions from individual slides were concatenated and integrated with the audio transcript, producing a comprehensive, sequentially accurate seminar transcript.

Literature Retrieval
Relevant literature was obtained via an automated agent querying the PubMed E-utilities API using the search term “Boon Lead Tee AND PPA.” Up to 100 records, comprising titles, abstracts, and PMIDs, were retrieved and stored in JSON format to facilitate downstream processes.

Draft Generation
A manuscript draft was produced by an agent ingesting the unified transcript, leveraging the o1-2024-12-17 language model. Instructions specified generating a coherent first draft while maintaining scientific accuracy and the original narrative voice, explicitly excluding any content absent from the original transcripts.

Citation Scaffolding and Review
Initial citations were scaffolded by employing GPT-4o-2024-08-06 to insert “[REF]” tokens immediately after statements necessitating citation. The manuscript then underwent three iterative Review–Improve cycles. Each cycle involved structured feedback on narrative coherence, factual accuracy, and completeness of citations, provided by a review agent. Feedback was addressed by an improvement agent utilizing the o1-2024-12-17 model, ensuring modifications were restricted to structural and stylistic enhancements, aligning strictly with reviewer recommendations.

Reference Resolution and Ranking
After iterative refinements, citation placeholders were algorithmically resolved by matching each “[REF]” placeholder to the most semantically relevant publication from the retrieved PubMed literature. This involved calculating semantic similarity scores between manuscript statements requiring citations and the PubMed abstracts, selecting the best match for each placeholder. Citations were then formatted to include author, year, and PMID details. Additionally, pivotal statements referencing Dr. Gorno-Tempini’s contributions were automatically identified and linked to the three most relevant APA-formatted citations, structured within a standardized JSON schema.

Outputs and Computational Resources
The automated pipeline generated a formatted, citation-rich manuscript, a ranked references JSON file, and comprehensive intermediate outputs for enhanced reproducibility. Processing was executed on an 8-vCPU virtual machine, requiring approximately 14 minutes per complete run (mean ± 45 s; n = 3). Audio transcription was the primary computational bottleneck (~6 minutes), with Review–Improve cycles collectively taking ~5 minutes; all other agent-based tasks individually required less than 60 seconds.

This modular, multi-agent methodology facilitated a systematic, transparent, and auditable transformation of seminar materials into a manuscript suitable for peer review, clearly delineating each stage from initial content ingestion through drafting, reviewing, and citation management.