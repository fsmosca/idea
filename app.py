"""
pip install streamlit
pip install spacy
python -m spacy download en_core_web_md
"""

import streamlit as st
import spacy
import pandas as pd
import time
from st_aggrid import AgGrid


def get_similarity(nlp, str1, str2):
    doc1 = nlp(str1)
    doc2 = nlp(str2)
    doc1 = nlp(' '.join([str(t) for t in doc1 if not t.is_stop]))
    doc2 = nlp(' '.join([str(t) for t in doc2 if not t.is_stop]))
    return doc1.similarity(doc2)


# @st.cache  # Buggy
def convert_df(df):
     return df.to_csv(index=False).encode('utf-8')


def download(df):
    csv = convert_df(df)
    st.download_button(
         label="Download data as CSV",
         data=csv,
         file_name='similarity.csv',
         mime='text/csv',
     )


def main():
    nlp = spacy.load("en_core_web_md")
    df = pd.DataFrame()

    tab1, tab2 = st.tabs(['Guide', 'Similarity'])

    with tab1:
        st.write('##### Guide')

        st.markdown(f'''
        Press the **Similarity** tab and enter text line by line. Each line
        will be compared to other lines and measure its similarity.

        100 could be fine but as number of lines increases the time to
        finish also increases.

        The similarity is measured using [spacy](https://spacy.io/usage/linguistic-features#vectors-similarity) en_core_web_md file.
        ''')

    with tab2:
        st.write('##### Similarity')

        with st.form('form', clear_on_submit=False):
            userinput = st.text_area(
                'Input text')
            cutoff = st.slider(
                'Similarity cutoff',
                min_value=0.0,
                max_value=1.0,
                value=0.95,
                help='If value is 0.95, similarity below that value will not be saved.')
            isstart = st.form_submit_button()

        with st.spinner('Processing ...'):
            if userinput and isstart:
                start_t = time.perf_counter()

                inputlist = userinput.split('\n')
                processlist = [i for i in inputlist if i]

                st.write(f'Number of rows of process: {len(processlist)}')
                data = []
                for i, t1 in enumerate(processlist):
                    for j, t2 in enumerate(processlist):
                        if i >= j:
                            continue
                        sim = get_similarity(nlp, t1, t2)
                        if sim >= cutoff:
                            data.append([t1, t2, sim])

                df = pd.DataFrame(data, columns = ['t1', 't2', 'sim'])
                df = df.sort_values(by=['sim'], ascending=[False])
                df = df.reset_index(drop=True)

                st.write(f'Number of rows saved: {len(df)}')
                AgGrid(df)
                # st.dataframe(df, height=300)

                st.write(f'elapse: {time.perf_counter() - start_t:0.1f}s')

        if len(df):
            download(df)


if __name__ == '__main__':
    main()
