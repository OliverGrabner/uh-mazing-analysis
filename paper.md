Uh-Mazing Speech Translation: A Multilingual Disfluency-Aware Benchmark
Maria Teleki ID 1,∗,∗∗, Maike Z¨ufle ID 2,∗,∗∗, Xiangjue Dong ID 1, Fabian Retkowski ID 2, Vil´em Zouhar3,
Joyce Nabende ID 4, James Caverlee ID 1
1 Dept. of Computer Science & Engineering, College Station, Texas, U.S.A., Texas A&M University
2 Institute for Anthropomatics and Robotics, Karlsruhe, Germany, KIT
3 ETH Zurich, Switzerland
4 Address Affiliation 4, Uganda, Makerere University
mariateleki@tamu.edu, maike.zuefle@kit.edu
Abstract
Spontaneous speech is rich in disfluencies such as filled pauses,
repetitions, and self-repairs, yet most speech translation sys-
tems are optimized for fluent, written-style input and often mis-
handle these phenomena. As a result, translations may omit
disfluencies leading to degraded meaning preservation and un-
natural outputs – especially in multilingual settings. We in-
troduce Uh-Mazing Speech Translation, a multilingual bench-
mark designed to systematically study how modern translation
models handle disfluent speech. The benchmark comprises
spontaneous speech across multiple global target languages,
with fine-grained annotations capturing disfluency types (INTJ,
PRN, EDITED). Using this benchmark, we analyze disfluency-
specific failure modes, including repetition amplification, cutoff
errors, and undertranslation. We further explore inference-time
strategies – such as XYZ – to improve disfluency handling with-
out retraining. Finally, we discuss cross-linguistic variation in
disfluency realization and outline evaluation methodologies tai-
lored to disfluency-aware translation. Our findings reveal sys-
tematic weaknesses in current systems and provide a founda-
tion for more robust, linguistically grounded speech translation
of spontaneous, real-world speech.
Index Terms: disfluency, translation, multilingual
1. Introduction
Spontaneous speech is disfluent [1]. Filled pauses, repetitions,
false starts, and self-repairs occur frequently in natural conver-
sation and reflect underlying cognitive and discourse processes.
While such phenomena are visible to human listeners, they pose
persistent challenges for automatic speech processing systems
[2, 3], to the point that platforms exist specifically for human-
powered verbatim transcription which retains disfluencies [4].
important applications: smart glasses with in-ear/visual real-
time translation [5, 6, 7]
other relevant usecases we discussed: Subtitling/dubbing,
authentic TTS
when you leave out disfluencies, you leave out important
cognitive/emotional indicators (add cites)
Most contemporary LLMs are trained on predominantly
cleaned and edited text, treating disfluency as noise [8]. As a
result, these systems often normalize disfluent speech, leading
to degraded translations that can misrepresent speaker intent,
disrupt timing cues, or introduce errors. This mismatch is par-
ticularly pronounced in multilingual speech translation, where
*These authors contributed equally.
**indicates the corresponding author.lungs
k
m
b
ug
n
m
u
u
ps glottis vocal tract
nasal tract
Figure 1: placeholder for concept figure – thinking we can show
disfluent text, audio/text, fluency labels, languages... describe
the dataset
disfluency realizations and their pragmatic roles vary substan-
tially across languages.
Recent progress in SpeechLLMs [9] offers a promising path
forward by reducing reliance on intermediate text representa-
tions and operating directly on speech signals. However, de-
spite their potential, it remains unclear how well these models
handle disfluencies in practice. Existing benchmarks and eval-
uation protocols largely focus on fluent speech or implicitly re-
ward disfluency removal, providing limited insight into model
behavior under realistic, conversational conditions.
In this work, we introduce Uh-Mazing Speech Translation,
a multilingual benchmark designed to stress-test speech trans-
lation systems—particularly SpeechLLMs—on disfluent, spon-
taneous speech. The benchmark comprises carefully curated
speech segments across multiple languages, with fine-grained
annotations capturing disfluency types, contextual dependen-
cies, and human judgments of translation quality. This de-
sign enables controlled evaluation of translations with and with-
out conversational context and supports systematic analysis of
disfluency-specific failure modes.
Using this benchmark, we analyze how current speech
translation models handle disfluencies, identifying recurring er-
rors such as repetition amplification, cutoff mishandling, and
undertranslation. Beyond analysis, we explore inference-time
strategies that improve disfluency handling without retraining,
providing practical guidance for deploying SpeechLLMs in
real-world, conversational settings. We contribute:
• Uh-Mazing Speech Translation, a multilingual, disfluency-
aware benchmark for evaluating speech translation on spon-
taneous speech; all code and data are available at TBA.
• An initial disfluency dictionary mapping the space of dis-
fluencies across languages.
Table 1: Multilingual benchmarks lack disfluency coverage.
Benchmark Name Spontaneous
Speech
Disfluency
Labels
#Lang.
Fisher-CALLHOME [10] ✓ ✗ 2
XTREME [11] ✗ ✗ 26
Common Voice [12] ✗ ✗ 38
Spontaneous Speech [13] ✓ ✗ 64
Uh-Mazing (ours) ✓ ✓ 11
• A taxonomy of disfluency-specific failure modes in current
speech translation and SpeechLLM systems.
• Inference-time strategies that improve robustness to dis-
fluencies without additional training.
2. Uh-Mazing Speech Translation
We publicly release the Uh-Mazing dataset and experimental
code at gihub-url.
2.1. Disfluency Annotations
For the Switchboard dataset, we align the textual transcripts
(LDC99T42) [14, 15] with the corresponding audio record-
ings (LDC97S62) [16]. Disfluency annotations provided in
the original Switchboard transcripts are retained and mapped
onto the aligned speech segments. Following established con-
ventions [1], we focus on three broad classes of disfluencies:
interjections (INTJ), parentheticals (PRN), and edited speech
(EDITED).
2.2. Human Translation
Human translations were obtained via Prolific1 for {ZH, ES, HI,
FR, DE, IT, CS, AR}, and by a team of local linguists for {SW,
LG}. The dataset consists of 800 samples — 80 per language,
which were divided into batches of 20 to mitigate annotator fa-
tigue. Each task was estimated to require approximately one
hour to complete, and Prolific annotators were compensated at
a rate of $12 USD per hour. A privacy policy covering data
handling and consent is provided in the project repository; no
personally identifiable information was collected, all data were
anonymized prior to release, and annotators could opt out at any
time.
Inter-annotator agreement is computed on five randomly
sampled instances annotated by the authors and external anno-
tators recruited through the authors’ professional network. We
find X agreement with the Prolific annotators (mean, min, max,
std), indicating ...
2.3. Data & Languages
The dataset is comprised of 80 samples from the Switchboard
dataset [14] translated: English → L ={Mandarin Chinese
(ZH), Spanish (ES), Hindi (HI), French (FR), German (DE),
Italian (IT), Swahili (SW), Czech (CS), Arabic (AR), Lu-
ganda (LG)}, yielding a total of 800 samples. Target lan-
guages were chosen to span diverse language families and re-
gions across all inhabited continents, enabling analysis of how
disfluency realization and translation behavior vary across typo-
logically and culturally distinct languages.
1Prolific is an academic crowdsourcing platform for participant re-
cruitment: www.prolific.com.
Each sample consists of a source utterance and its transla-
tion, represented in both speech and text modalities. We denote
text by t and speech by s. Formally, the dataset is represented
as
D = (tsrc, ssrc, ttgt, stgt, Li)N
i=1, (1)
where N = 800 is the total number of source–target pairs and
Li ∈ L denotes the target language of the i-th sample. Each
sample has fluent (f superscript) and disfluent (d superscript)
versions.
2.4. Target Language Speech Synthesis via TTS
To support SpeechLLM evaluation, we generate target-
language speech by synthesizing audio from translated target
text using off-the-shelf TTS systems. This design choice re-
flects a synthetic-data methodology: fine-grained disfluency an-
notations are only available for English spontaneous speech (via
Switchboard), and comparable annotated resources do not exist
at scale for target languages. As a result, synthesizing target-
language speech is necessary to preserve controlled disfluency
structure across languages while enabling evaluation in both
text and speech modalities.
3. Models & Evaluation
3.1. Translation Models
We evaluate four types of models for speech translation: (1)
Cascaded models that combine separate transcription and trans-
lation systems, (2) End-to-end models that directly translate
speech without intermediate text, (3) Speech LLMs that leverage
multimodal large language models, and (4) Commercial models
from leading API providers.
Cascaded Models We use Canary canary-1b-v22 [17]
and Whisper openai/whisper-large-v33 [18] to tran-
scribe the audio, then translate using Tower-Plus-9B4 [19]
and Llama-3.1-8B-Instruct5 [20]. We also evaluate
Llama and Tower on human-annotated transcripts to measure
the impact of transcription errors on translation quality.
End-to-End Models We evaluate Canary and Whisper as
end-to-end speech translation models. Note that Canary does
not support Chinese, Hindi, Swahili, Arabic, or Luganda.
Speech LLMs We evaluate
Phi-4-multimodal-instruct6 [21] and
Qwen2.5-Omni-7B7 [22] as multimodal speech LLMs.
Commercial Models We evaluate ChatGPT and Gemini
with both speech input and human-annotated gold transcripts.
3.2. Prompts
We evaluate models using two prompting strategies: (1) a
standard prompt that requests direct translation, and (2) a
disfluency-aware prompt that explicitly instructs the model to
preserve disfluencies such as filled pauses (e.g., ”um”, ”uh”),
repetitions, and hesitations in the translation. The prompts are
defined as follows:
• Standard: ”Listen to the following audio and translate the
speech into {target language} text.”
2 nvidia/canary-1b-v2
3 openai/whisper-large-v3
4 Unbabel/Tower-Plus-9B
5 meta-llama/Llama-3.1-8B-Instruct
6 microsoft/Phi-4-multimodal-instruct
7 Qwen/Qwen2.5-Omni-7B
Figure 2: Taxonomy of disfluency-specific failure modes.
Failure Modes
ASR Fallback
partial translation
partial translation
partial translation
Collapse Into
Repetition
fixation on filled pauses or partial
words
fixation on filled pauses or partial
words
Disfluency
Deletion
–
–
–
• Disfluency-aware: ”Listen to the following audio and trans-
late the speech into {target language} text, keeping
any disfluencies (such as ’um’, ’uh’, repetitions, and hesi-
tations) in the translation.”
We apply both prompts to cascaded models, Speech LLMs,
and commercial models. End-to-end models are not evaluated
with different prompts as they are not designed to follow such
instructions.
3.3. Evaluation
We evaluate models along two complementary dimensions:
overall translation quality and disfluency preservation.
Translation Quality. We assess standard translation quality us-
ing BLEU [23] and COMET-Kiwi [24], which measure how
well the translated output captures the meaning and fluency of
the reference translations.
Disfluency Preservation. To evaluate whether models correctly
preserve disfluencies in the translation, we employ three ap-
proaches: (1) LLM-as-a-judge using {model name} to assess
the presence and accuracy of disfluencies in translations, (2) E-
Scores, and (3) Z-Scores [25], which specifically measure the
retention of disfluent elements from source to target.
4. Results
4.1. A Taxonomy of Disfluency-Specific Failure Modes
Figure 2
4.2. Disfluency Type (INTJ/PRN/EDITED) Ablation
- error rates - which type causes which failure mode - also all
out fluent vs. disfluent
4.3. Performance Across Languages
- kinda by continent - which languages have good/bad disflu-
ency translation performance
4.4. ASR+LLM vs. SpeechLLM Performance
4.5. Human Evaluation
5. Inference-Time Interventions
Post-training models to improve robustness to disfluencies re-
duces generalization capabilities [26]. For this reason, we focus
on inference-time interventions that improve handling of disflu-
ent input without modifying model parameters [27].
We investigate a set of lightweight inference-time strategies
aimed at mitigating disfluency-specific failure modes identified
in Section 4.1. These interventions act by constraining decod-
ing behavior or restructuring model inputs in order to preserve
disfluency-related information while reducing undesirable be-
haviors such as repetition collapse or unintended normalization.
As they do not require retraining, the proposed methods can
be applied directly to existing speech translation systems and
SpeechLLMs.
This setting reflects common deployment scenarios in
which models are applied to conversational or spontaneous
speech, but retraining is infeasible or undesirable. In such cases,
inference-time interventions offer a practical mechanism for
adapting model behavior to disfluent speech while largely pre-
serving performance on fluent inputs. Our experiments show
that targeted inference-time strategies can improve disfluency
handling with minimal impact on overall translation quality.
6. Recommendations
Based on our findings, we make three practical deployment rec-
ommendations:
▷ Recommendation 1:
▷ Recommendation 2:
▷ Recommendation 3:
7. Discussion & Limitations
Disfluencies exhibit language-specific realizations; for exam-
ple, discourse markers such as “you know” are frequent in En-
glish but may not have direct equivalents in other languages.
Consequently, literal translation of disfluent segments may not
align with how disfluencies are typically expressed in the target
language.
8. Generative AI Use Disclosure
Generative AI tools were used to assist with drafting and refin-
ing portions of the manuscript, as well as for coding and figure
preparation. All scientific content, analyses, and conclusions
were developed and verified by the authors.
