import streamlit as st
from openai import OpenAI
import re

DEFAULT_PARAGRAPH='''
Ali is a friend of Kevin, they both studied in Sydney. After finishing their studies, Ali moved to America to work in IBM and Kevin moved to Malaysia to work in Oracle
'''

DEFAULT_ONTOLOGY='''
object:Person {name, age}
object:Country {name}
object:Company {name}

relation:FRIENDS_WITH (Person -> Person)
relation:LIVES_IN (Person -> Country)
relation:LOCATED_IN (Company -> Country)
'''
client = OpenAI()

# Set your OpenAI API key here

def generate_cypher_query(paragraph, ontology):
    system_prompt = f"""
    You are a software that generate cypher query to populate a
    knowledge graph based on the provided ontology. User will 
    provide the text content to be converted. Following is the ontology.

    -- start of ontology 
    {ontology}
    -- end of ontology
    """

    try:
        response = client.chat.completions.create(
                model="gpt-4o",  # You can change the model if necessary
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': paragraph}
                ],
                n=1,
                stop=None,
                temperature=0.3)

        cypher_code = response.choices[0].message.content.strip()
        m = re.match(r'.*?```cypher\n(.*)```.*?', cypher_code, re.DOTALL)
        if not m:
            m = re.match(r'.*?```(.*)```.*?', cypher_code, re.DOTALL)
        if not m:
            return "Generated code does not have cypher query"

        return m.group(1)
    except Exception as e:
        return f"An error occurred: {e}"

css = '''
<style>
    [data-testid="stSidebar"]{
        width: 400px;
        min-width: 400px;
        max-width: 600px;
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)
# Streamlit app setup
st.title("Knowledge Graph Cypher Query Generator")

# Sidebar for input collection
st.sidebar.header("Input Parameters")

paragraph = st.sidebar.text_area("Enter the text paragraph:", height=300, value=DEFAULT_PARAGRAPH)
ontology = st.sidebar.text_area("Enter the ontology definition:", height=300, value=DEFAULT_ONTOLOGY)

if st.sidebar.button("Submit"):
    if paragraph and ontology:
        # Generate the Cypher query using OpenAI
        cypher_query = generate_cypher_query(paragraph, ontology)

        # Display the generated Cypher query
        st.subheader("Generated Cypher Query")
        st.code(cypher_query, language='cypher')
    else:
        st.error("Please provide both the text paragraph and the ontology definition.")

