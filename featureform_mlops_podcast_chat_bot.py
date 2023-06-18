import featureform as ff
from sentence_transformers import SentenceTransformer
from featureform import local
import codecs
!pip install pinecone-client

client = ff.Client(local=True)

# Determine the encoding of the file (replace 'latin1' with the encoding of your file)
with codecs.open('/content/drive/MyDrive/mediglot_files/myringoplasty_consent_form.txt', 'r', encoding='latin1') as f:
    content = f.read()

# Write the content back to the file in 'utf-8'
with codecs.open('/content/drive/MyDrive/mediglot_files/myringoplasty_consent_form.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# Determine the encoding of the file (replace 'latin1' with the encoding of your file)
with codecs.open('/content/drive/MyDrive/mediglot_files/tympanoplasty_consent_form.txt', 'r', encoding='latin1') as f:
    content = f.read()

# Write the content back to the file in 'utf-8'
with codecs.open('/content/drive/MyDrive/mediglot_files/tympanoplasty_consent_form.txt', 'w', encoding='utf-8') as f:
    f.write(content)

forms = local.register_directory(
    name="consent_forms",
    path="mediglot_files",
    description="Pre-Op Consent Forms",
)

client.dataframe(forms)

@local.df_transformation(inputs=[forms])
def primary_key(forms_df):
    forms_df["PK"] = range(len(forms_df))

    return forms_df

df = client.dataframe(primary_key)

df.head()

@local.df_transformation(inputs=[primary_key])
def vectorize_comments(forms_df):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(forms_df["body"].tolist())
    forms_df["vector"] = embeddings.tolist()

    return forms_df

pinecone = ff.register_pinecone(
    name="pinecone",
    project_id='-nye7wmybfxueff8owfp',
    environment='asia-southeast1-gcp-free',
    api_key='0dae6322-7ead-4767-8c2a-6e45d7362eae',
)

client.apply()

@ff.entity
class Forms:
    form_embeddings = ff.Embedding(
        vectorize_comments[["PK", "vector"]],
        dims=384,
        vector_db=pinecone,
        description="Embeddings created text of the forms",
        variant="v2"
    )
    forms = ff.Feature(
        primary_key[["PK", "body"]],
        type=ff.String,
        description="Original form content",
        variant="v2"
    )

client.apply()

@ff.ondemand_feature(variant="calhacks")
def relevent_docs(client, params, entity):

    model = SentenceTransformer("all-MiniLM-L6-v2")
    search_vector = model.encode(params["query"])
    res = client.nearest("form_embeddings", "v2", search_vector, k=1)
    return res

client.apply()
client.features([("relevent_docs", "calhacks")], {}, params={"query": "enterprise MLOps"})

@ff.ondemand_feature(variant="calhack")
def contextualized_prompt(client, params, entity):
    pks = client.features([("relevent_docs", "calhacks")], {}, params=params)
    prompt = "Use the following snippets from our podcast to answer the following question\n"
    for pk in pks[0]:
        prompt += "```"
        prompt += client.features([("comments", "v2")], {"speaker": pk})[0]
        prompt += "```\n"
    prompt += "Question: "
    prompt += params["query"]
    prompt += "?"
    return prompt

client.apply()
client.features([("contextualized_prompt", "calhack")], {}, params={"query": "enterprise MLOps"})

"""# Finally we can feed our prompt into OpenAI!"""

client.apply()
q = "What should I know about MLOps testing"
prompt = client.features([("contextualized_prompt", "calhack")], {}, params={"query": q})[0]
import openai
openai.organization = os.getenv("OPENAI_ORG", "")
openai.api_key = os.getenv("OPENAI_KEY", "")
print(openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    max_tokens=1000, # The max number of tokens to generate
    temperature=1.0 # A measure of randomness
)["choices"][0]["text"])