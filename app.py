import streamlit as st
import nltk
import spacy
import pickle
nltk.download('stopwords')


import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
import os
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from streamlit_tags import st_tags

clf = pickle.load(open('uclf.pkl','rb'))
word_vectorizer = pickle.load(open('uword_vectorizer.pkl','rb'))

# Load the pre-trained model and tokenizer
df = pd.read_csv('./new_recommend.csv')
df.rename(columns = {'Skills (Keywords for Resume)':'skills'}, inplace = True)

def predict(cleaned_resume):
    input_features = word_vectorizer.transform([cleaned_resume])
    prediction_id = clf.predict(input_features)[0]
    return prediction_id

def catego(prediction):
       category = {
            0: "Java Developer",
            1: "HR",
            2: "Database Engineer",
            3: "Advocate",
            4: "Data Science",
            5: "DevOps Engineer",
            6: "Testing Engineer",
            7: "DotNet Developer",
            8: "Hadoop",
            9: "Automation Testing",
            10: "Civil Engineer",
            11: "Arts",
            12: "Health and fitness	",
            13: "Business Analyst	",
            14: "Python Developer",
            15: "SAP Developer",
            16: "Electrical Engineering	",
            17: "ETL Developer	",
            18: "Blockchain",
            19: "Mechanical Engineer",
            20: "Network Security Engineer",
            21: "Sales",
            22: "Operations Manager",
            23: "Web Designing",
            24: "PMO",
        }
       category_name = category.get(prediction, "Unknown")
       return category_name





def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def rlist(category_name):
  category = category_name
  results = df.loc[df["Domain"] == category]
  one = results['skills']
  llist = one.tolist()
  return llist

def tok(llist):
  corpus = " "
  for i in range(0, len(llist)):
    corpus = corpus + str(llist)

  tokenizer = nltk.tokenize.RegexpTokenizer('\w+')
    # Tokenizing the text
  tokens = tokenizer.tokenize(corpus)

  words = []
    # Looping through the tokens and make them lower case
  for word in tokens:
    words.append(word.lower())

  return words

def main():
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])

        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                resumestext = resume_text.lower()


                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''', unsafe_allow_html=True)


                listToStr = ' '.join([str(elem) for elem in resume_data["skills"]])
                prediction = predict(listToStr)
                category_name = catego(prediction)
                st.write("Predicted Category:", category_name)



                 ## Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'] , key='1')



                ## Recommended Skill shows
                llist = rlist(category_name)
                uprecom = tok(llist)

                newrecom = []
                for i in uprecom:
                   if i != 'law':
                      newrecom.append(i)
                        # print(newarr)
                        # print(i)
                   else:
                      continue

                newrecommend = []

                for j in range(0,len(newrecom)-15):
                    newrecommend.append(newrecom[j])

                keywords = st_tags(label='### Recommended Skills ',
                                   text='See our skills recommendation',
                                   value=newrecommend )

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'objective' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html=True)

                if 'certifications' or 'certificates' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Certifications✍/h4>''',
                        unsafe_allow_html=True)
                elif 'courses' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Courses ✍/h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add certification or courses you have learned ✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html=True)

                if 'hobbies' or 'interests' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html=True)

                if 'achievements' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html=True)

                if 'projects' in resumestext:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")
                st.balloons()






if __name__ == "__main__":
  main()