import re

AI_RULES = [
    (r"^(ml ?ops|mlops.*|machine learning (\(ml\) )?op(s|erations).*|llmops)$", "MLOps"),
    (r"^(azure (machine learning|ml)|azure ai.*|azure openai)$", "Azure ML / AI"),
    (r"^(vertex ?\.?ai|google vertex ai)$", "Vertex AI"),
    (r"^(sagemaker|aws sagemaker|amazon sagemaker)$", "SageMaker"),
    (r"^(large language models?.*|llms?|llm .*|gpt.*|chatgpt|openai|gen(erative)? ai.*|generative models?|generative modell?ing)$", "Generative AI / LLMs"),
    (r"^(natural language processing.*|nlp|natural language understanding|natural language generation|nlu|text mining|text analytics)$", "NLP"),
    (r"^(computer vision.*|image processing|object detection|image recognition)$", "Computer Vision"),
    (r"^(reinforcement learning.*)$", "Reinforcement Learning"),
    (r"^(deep learning.*|neural networks?.*|neural nets|deep neural networks|artificial neural networks|convolutional neural networks.*|cnns?|recurrent neural networks.*|rnns?|graph neural networks)$", "Deep Learning"),
    (r"^(transformers?|transformer models|bert|hugging ?face|huggingface transformers)$", "Transformers / Hugging Face"),
    (r"^(langchain|llamaindex|vector databases?|rag|retrieval augmented generation)$", "LangChain / RAG"),
    (r"^(tensorflow.*|tf)$", "TensorFlow"),
    (r"^(pytorch.*|torch)$", "PyTorch"),
    (r"^(keras)$", "Keras"),
    (r"^(scikit ?-?learn|scikitlearn|sklearn|scikit)$", "scikit-learn"),
    (r"^(xgboost|lightgbm|catboost|gradient boosting)$", "Gradient Boosting (XGBoost)"),
    (r"^(responsible( and explainable)? ai|explainable ai|ethical ai|ai ethics|xai)$", "Responsible / Explainable AI"),
    (r"^(predictive model(l)?ing|predictive models|predictive analytics)$", "Predictive Modeling"),
    (r"^(artificial intelligence.*|ai)$", "Artificial Intelligence"),
    (r"^(machine learning.*|ml|ai ?/ ?ml|ml ?/ ?ai|ai/machine learning)$", "Machine Learning"),
]
AI_RULES = [(re.compile(p), label) for p, label in AI_RULES]
AI_SKILLS = sorted({label for _, label in AI_RULES})

ALIASES = {
    "problemsolving": "problem solving", "problem-solving": "problem solving",
    "communication skills": "communication", "written and verbal communication": "communication",
    "amazon web services": "aws", "microsoft azure": "azure", "google cloud platform": "gcp",
    "google cloud": "gcp", "apache spark": "spark", "pyspark": "spark", "powerbi": "power bi",
    "ms excel": "excel", "microsoft excel": "excel", "statistical analysis": "statistics",
    "statistical modeling": "statistics", "docker containers": "docker", "kubernetes (k8s)": "kubernetes",
    "data visualisation": "data visualization", "c/c++": "c++", "git/github": "git", "github": "git",
}

STOPLIST = {
    "communication", "teamwork", "collaboration", "problem solving", "leadership",
    "attention to detail", "analytical skills", "time management", "critical thinking",
    "bachelor's degree", "master's degree", "phd", "computer science", "engineering",
    "mathematics", "analytical thinking", "interpersonal skills", "organizational skills",
    "presentation skills", "mentoring", "customer service", "self-motivated", "adaptability",
    "creativity", "research", "documentation", "troubleshooting", "independent work",
    "verbal communication", "written communication", "teamwork and collaboration",
    "data science", "data analysis", "data analytics", "data engineering",
}


def clean_skill(raw):
    t = raw.strip().lower()
    t = re.sub(r"^[\*\-•\s]+", "", t)
    t = re.sub(r"\s+", " ", t)
    if not t or len(t) > 60:
        return None, False
    for pat, label in AI_RULES:
        if pat.match(t):
            return label, True
    t = ALIASES.get(t, t)
    if t in STOPLIST:
        return None, False
    return t, False


def parse_posting(skill_string):
    out = set()
    if not isinstance(skill_string, str):
        return out
    for raw in skill_string.split(","):
        label, _ = clean_skill(raw)
        if label:
            out.add(label)
    return out


def is_ai(label):
    return label in AI_SKILLS
