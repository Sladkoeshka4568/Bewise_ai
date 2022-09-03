import pandas as pd
import numpy as np
import re

df_test = pd.read_csv('test_data.csv')


def string_search(search_in_df, in_column, search_options):
    r = search_options
    search = search_in_df[in_column].apply(lambda x: re.search(r, str(x).lower()))
    result = np.all(np.array([~search.isnull()]), axis=0)
    result_name_df = search_in_df[result]
    return result_name_df


def company_search(text):
    start_keywords = 'компания'
    end_keywords = ['удобно', 'звоним', 'звоню']
    text = text.lower().split()
    try:
        start_ind = text.index(start_keywords)
        for i in end_keywords:
            if i in text:
                end_ind = text.index(i)
            else:
                continue
            return ' '.join(text[start_ind + 1:end_ind])
    except ValueError:
        return None


def name_search(text):
    keywords = ['зовут', 'да', 'это']
    count = 0
    text = text.lower().split()
    for i in text:
        if i in keywords:
            ind = text.index(i)
            count += 1
            if count == 2:
                return str(text[ind + 1])
                break
            if str(text[ind - 1]) == 'меня':
                return str(text[ind + 1])
                break
            if str(text[ind + 1]) == 'компания':
                return str(text[ind - 1])
                break

introduced_himself =r'(меня.*?зовут|да это|вас беспокоит)'
greeting =r'(добрый|здра|привет)'
parting =r'(до свид|до встр|до завтра)'

df_introduced_himself = string_search(df_test, 'text', introduced_himself).rename(columns={'text': 'introduced_himself'})
df_greeting = string_search(df_test, 'text', greeting).rename(columns={'text': 'greeting'})
df_parting = string_search(df_test, 'text', parting).rename(columns={'text': 'parting'})
df_introduced_himself = df_introduced_himself.query('role == "manager"')
df_greeting = df_greeting.query('role == "manager"').drop_duplicates('dlg_id')
df_parting = df_parting.query('role == "manager"')
df_greeting = df_greeting.drop(['line_n', 'role'], axis=1)
df_introduced_himself = df_introduced_himself.drop(['line_n', 'role'], axis=1)
df_parting = df_parting.drop(['line_n', 'role'], axis=1)

df_result = df_test[['dlg_id', 'role']]\
    .query('role == "manager"')\
    .drop_duplicates('dlg_id')
df_result = df_result.merge(df_greeting, how = 'left')\
            .merge(df_introduced_himself, how = 'left')\
            .merge(df_parting, how = 'left')


df_result['name_manager'] = df_result['introduced_himself'].apply(lambda x: name_search(str(x)))
df_result['name_company'] = df_result['introduced_himself'].apply(lambda x: company_search(str(x)))


df_result.to_csv('result.csv')
