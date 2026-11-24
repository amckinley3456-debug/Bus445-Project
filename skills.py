AI_SKILL_GROUPS = [
    ["MLOps",
     ["ml ops", "mlops", "llmops"],
     ["mlops", "machine learning ops", "machine learning operations",
      "machine learning (ml) ops", "machine learning (ml) operations"]],
    ["Azure ML / AI",
     ["azure machine learning", "azure ml", "azure openai"],
     ["azure ai"]],
    ["Vertex AI",
     ["vertexai", "vertex ai", "vertex.ai", "vertex .ai", "google vertex ai"],
     []],
    ["SageMaker",
     ["sagemaker", "aws sagemaker", "amazon sagemaker"],
     []],
    ["Generative AI / LLMs",
     ["llm", "llms", "chatgpt", "openai", "generative model", "generative models",
      "generative modeling", "generative modelling"],
     ["large language model", "llm ", "gpt", "gen ai", "generative ai"]],
    ["NLP",
     ["nlp", "natural language understanding", "natural language generation", "nlu",
      "text mining", "text analytics"],
     ["natural language processing"]],
    ["Computer Vision",
     ["image processing", "object detection", "image recognition"],
     ["computer vision"]],
    ["Reinforcement Learning",
     [],
     ["reinforcement learning"]],
    ["Deep Learning",
     ["neural nets", "deep neural networks", "artificial neural networks", "cnn", "cnns",
      "rnn", "rnns", "graph neural networks"],
     ["deep learning", "neural network", "convolutional neural networks",
      "recurrent neural networks"]],
    ["Transformers / Hugging Face",
     ["transformer", "transformers", "transformer models", "bert", "huggingface",
      "hugging face", "huggingface transformers"],
     []],
    ["LangChain / RAG",
     ["langchain", "llamaindex", "vector database", "vector databases", "rag",
      "retrieval augmented generation"],
     []],
    ["TensorFlow",
     ["tf"],
     ["tensorflow"]],
    ["PyTorch",
     ["torch"],
     ["pytorch"]],
    ["Keras",
     ["keras"],
     []],
    ["scikit-learn",
     ["scikitlearn", "scikit-learn", "scikit learn", "scikit -learn", "sklearn", "scikit"],
     []],
    ["Gradient Boosting (XGBoost)",
     ["xgboost", "lightgbm", "catboost", "gradient boosting"],
     []],
    ["Responsible / Explainable AI",
     ["responsible ai", "responsible and explainable ai", "explainable ai", "ethical ai",
      "ai ethics", "xai"],
     []],
    ["Predictive Modeling",
     ["predictive modeling", "predictive modelling", "predictive models",
      "predictive analytics"],
     []],
    ["Artificial Intelligence",
     ["ai"],
     ["artificial intelligence"]],
    ["Machine Learning",
     ["ml", "ai/ml", "ai / ml", "ai /ml", "ai/ ml", "ml/ai", "ml / ai", "ml /ai", "ml/ ai",
      "ai/machine learning"],
     ["machine learning"]],
]

AI_SKILLS = []
for group in AI_SKILL_GROUPS:
    AI_SKILLS.append(group[0])

ALIASES = {
    "problemsolving": "problem solving",
    "problem-solving": "problem solving",
    "communication skills": "communication",
    "written and verbal communication": "communication",
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "apache spark": "spark",
    "pyspark": "spark",
    "powerbi": "power bi",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "statistical analysis": "statistics",
    "statistical modeling": "statistics",
    "docker containers": "docker",
    "kubernetes (k8s)": "kubernetes",
    "data visualisation": "data visualization",
    "c/c++": "c++",
    "git/github": "git",
    "github": "git",
}

REMOVE = [
    "communication", "teamwork", "collaboration", "problem solving", "leadership",
    "attention to detail", "analytical skills", "time management", "critical thinking",
    "bachelor's degree", "master's degree", "phd", "computer science", "engineering",
    "mathematics", "analytical thinking", "interpersonal skills", "organizational skills",
    "presentation skills", "mentoring", "customer service", "self-motivated", "adaptability",
    "creativity", "research", "documentation", "troubleshooting", "independent work",
    "verbal communication", "written communication", "teamwork and collaboration",
    "data science", "data analysis", "data analytics", "data engineering",
]

def clean_skill(raw):
    skill = raw.strip().lower()
    skill = skill.lstrip("*-• \t\n")
    skill = " ".join(skill.split())

    if skill == "" or len(skill) > 60:
        return None

    for group in AI_SKILL_GROUPS:
        label = group[0]
        exact_names = group[1]
        starting_words = group[2]
        if skill in exact_names:
            return label
        for start in starting_words:
            if skill.startswith(start):
                return label

    if skill in ALIASES:
        skill = ALIASES[skill]

    if skill in REMOVE:
        return None

    return skill

def parse_posting(skills_text):
    skills = set()
    if type(skills_text) != str:
        return skills
    for raw in skills_text.split(","):
        skill = clean_skill(raw)
        if skill is not None:
            skills.add(skill)
    return skills

def is_ai(skill):
    return skill in AI_SKILLS
