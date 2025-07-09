import re
import os
from pdfminer.high_level import extract_text
from flask import Flask,render_template,request
from werkzeug.utils import secure_filename
from docx import Document
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')


app= Flask(__name__)
upload_folder='uploads'
app.config['UPLOAD_FOLDER']=upload_folder
stop_w = set(stopwords.words('english'))
os.makedirs(upload_folder, exist_ok=True)


keywords = ["python", "machine learning", "flask","sql","api","html","javascript","aws","cloud"]


def extract_from_pdf(filename):
    return extract_text(filename)       


def extract_from_word(filename):
    doc=Document(filename)

    parts = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            parts.append(text)
    
    return "\n".join(parts)


def clean(raw: str) -> str:
    txt = raw.lower()
    txt = re.sub(r'[^a-z\s]', ' ', txt)   # keep letters/spaces only
    return re.sub(r'\s+', ' ', txt).strip()


def score_cv(filename):
    ext=os.path.splitext(filename)[1].lower()
    if ext=='.pdf':
        rawtext=extract_from_pdf(filename)
    elif ext=='.docx':
        rawtext=extract_from_word(filename)
    else:
        raise ValueError("unsupported file")
    
    text=clean(rawtext)
    
    present=[]

    present, missing = [], []
    for i in keywords:
        pattern = r'\b' + re.escape(i.lower()) + r'\b'
        if re.search(pattern, text):
            present.append(i)
        else:
            missing.append(i)
    
    score=(len(present)/len(keywords))*100 
    val=round(score)
    if val>=90:
        comment="Strong match. Candidate fits the role very well."
    elif val>=75 and val<90:
        comment="Good match. Few improvements needed."
    elif val>=60 and val<75:
        comment="Decent match. Lacks some key skills."
    elif val>=40 and val<60:
        comment="Partial match. Missing several core keywords."
    elif val>=20 and val<40:
        comment="Weak match. Limited relevance to the role."
    else:
        comment="Poor match. Not suitable for this position."
        
    
    return present,missing,val,comment



@app.route("/",methods=['GET','POST'])
def home():
    if request.method=='POST':
        uploaded_file=request.files['cv']
        if uploaded_file:
            filename=secure_filename(uploaded_file.filename)
            filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            uploaded_file.save(filepath)

            present,missing,score,comment=score_cv(filepath)
            p= ", ".join(present)
            m= ", ".join(missing)
            
        return render_template('index.html',score=score,filename=filename,missing=m,present=p,comment=comment)
    
    return render_template("index.html", score=None, filename=None)


if __name__=="__main__":
    app.run(debug=True)

    
