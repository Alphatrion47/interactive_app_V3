#Screening and Team selection functionality with excel,csv and pdf
# Primary search with spacy

import streamlit as st
import pandas as pd
from groq import Groq
from PyPDF2 import PdfReader
import spacy
from nltk.stem.snowball import SnowballStemmer

nlp = spacy.load('en_core_web_sm')
stemmer = SnowballStemmer("english")

client = Groq(api_key= st.secrets["groq_passkey"])

st.title("Interactive Selection")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "df" not in st.session_state:
    st.session_state.df = None

if "keyword" not in st.session_state:
    st.session_state.keyword = None

if "task" not in st.session_state:
    st.session_state.task = None

uploaded_file = st.file_uploader("Choose a file with information. Acceptable formates are pdf,excel and csv:",type =["csv","xlsx","xls","pdf"])

def file_reader(file):
# Function to extract text from file formats
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text_data = []
        for num,page in enumerate(reader.pages):
            text = page.extract_text()
            text_data.append({"page": num+1, "details": text})
            text_df = pd.DataFrame(text_data)
        return text_df
    else:
        return pd.read_excel(file)


if uploaded_file:
    st.write("File preview")
    try:    
        st.session_state.df = file_reader(uploaded_file)
        st.dataframe(st.session_state.df.head(5))
        st.write("There are {} total candidates.".format(len(st.session_state.df)))
    except Exception as ex:
        st.error("Failed to read file due to the following reasons:",ex)

    st.header("Select Task")    
    st.session_state.task = st.radio("Options: ",["Screening chatbot","Chatbot"],index = None)


if st.session_state.task == "Screening chatbot":
    st.write("Select the primary criteria")
    column = st.selectbox("Columns",st.session_state.df.columns)

    if st.session_state.df[column].dtype =="object":
        st.session_state.keyword = st.text_input("Enter the keyword criteria for screening (eg: MLops, sql, etc.)")
        if st.session_state.keyword:
            filtered_df = st.session_state.df[st.session_state.df[column].str.contains(st.session_state.keyword,case = False, na= False)]
            st.session_state.mydf = filtered_df
            st.dataframe(st.session_state.mydf)
            st.write("Candidate list filtered succesfully")
            st.write("There are {} total candidates, having {} skillset.".format(len(st.session_state.mydf),st.session_state.keyword))
            
    else:
        st.session_state.mydf = st.session_state.df
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Enquire about the candidates")  

    

    if user_prompt:
        #Prompt for querying from candidate list
        st.chat_message("user").markdown(user_prompt)  
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})  

        full_prompt = f"""
        You are an advanced data analysis model designed to provide precise and consistent answers based on the given DataFrame {st.session_state.mydf.to_string()}

        Question to respond: {user_prompt}

        If retreval of records is required, present the records with all relevant details in a tabular format.
        
        """
        chat = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature = 0.5
        )

        assistant_response = chat.choices[0].message.content  
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})  

        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    


if st.session_state.task == "Chatbot":
#Primarily for pdf input
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Enquire about the uploaded file")
        
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)  
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})  

        full_prompt = f"""
        You are a helpful assistant who assists the user in retreiving relevant information from the given document {st.session_state.mydf.to_string()}.
        Keep the answer as relevant and logical as possible.

        Question to respond: {user_prompt}

        Respond in detail and in tabular format when required.
        
        """
        chat = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama3-8b-8192",
            temperature = 0.5
        )

        assistant_response = chat.choices[0].message.content  
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})  

        with st.chat_message("assistant"):
            st.markdown(assistant_response)













        # screening_chatbot = True
    # else:
    #     team_size = st.slider("Slide and select the number of members required in project",min_value = 1,max_value = st.session_state.total_candidates)
    #     st.write("Requirement is for a {} member team.".format(team_size))
    #     st.session_state.size = team_size
        # team_chatbot = True






# if team_chatbot:
#     for message in st.session_state.chat_history:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     user_prompt = st.chat_input("What is the purpose of the team ?")

#     if user_prompt:
#         st.chat_message("user").markdown(user_prompt)  
#         st.session_state.chat_history.append({"role": "user", "content": user_prompt})  

#         full_prompt = f"""
#         You are an advanced assistant to a manager. Tasked with helping him plan and build his team, you have to provide precise and consistent answers based on the given DataFrame {st.session_state.df.to_string()}

#         Question to respond: {user_prompt}

#         Present the records with closest match to the question.

#         Finally, provide the reasoning behind your answer and advise on improvements.
        
#         """
#         chat = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": full_prompt,
#                 }
#             ],
#             model="llama3-8b-8192",
#             temperature = 0.5
#         )

#         assistant_response = chat.choices[0].message.content  
#         st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})  

#         with st.chat_message("assistant"):
#             st.markdown(assistant_response)