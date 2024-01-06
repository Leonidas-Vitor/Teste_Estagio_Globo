import pandas as pd
import numpy as np
import requests
from io import StringIO
import streamlit as st
from st_pages import Page, show_pages, add_page_title
import plotly.express as px

def GetBasicTextMarkdown(font_size: float, text: str, align = 'center'):
    return f"""<p style='text-align: {align}; font-size:{font_size}px;'><b>{text}</b></p>"""

def SetPageConfig(title='Teste estágio'):
    st.set_page_config(
        page_title=title,
        page_icon="globoPlayIcon.png",
        layout="wide",
        initial_sidebar_state = "expanded")
    
SetPageConfig()

html_p = """<p style='text-align: center; font-size:%spx;'><b>%s</b></p>"""

st.markdown('''<h1 style='text-align: center; '><b>Programa Estagiar Globo 2023</b></h1>''',unsafe_allow_html = True)

st.divider()

email = '''leonidas.vitor@outlook.com'''
github_link = '''https://github.com/Leonidas-Vitor'''

columns = st.columns([0.6,0.4])
with columns[0]:
    st.markdown(html_p % tuple([25,'Candidato: Leônidas Almeida']),unsafe_allow_html = True)
    st.markdown(html_p % tuple([25,f'E-mail: <a href= mailto:{email}>{email}</a>']),unsafe_allow_html = True)
    st.markdown(html_p % tuple([25,f'GitHub: <a href={github_link}>{github_link}</a>']),unsafe_allow_html = True)
with columns[1]:
    st.image('globoPlayIcon.png',width=400)

st.subheader('Dados',divider=True)

@st.cache_data
def get_data():
    url = 'https://api.onedrive.com/v1.0/shares/s!Asuw4D2AHTOZlYc5XMBSbZydZF8WQw/root/content'
    result = requests.get(url)

    df_conteudo = pd.read_csv(StringIO(result.text), sep=';')

    url = 'https://api.onedrive.com/v1.0/shares/s!Asuw4D2AHTOZlYc7rk_HkK02f4T2GA/root/content'
    result = requests.get(url)

    df_play = pd.read_csv(StringIO(result.text), sep=';')

    return df_play.merge(df_conteudo, on='id_conteudo', how='left')

df = get_data()

with st.expander('Código',expanded=True):
    st.code(
    ''' 
    url = 'https://api.onedrive.com/v1.0/shares/s!Asuw4D2AHTOZlYc5XMBSbZydZF8WQw/root/content'
    result = requests.get(url)

    df_conteudo = pd.read_csv(StringIO(result.text), sep=';')

    url = 'https://api.onedrive.com/v1.0/shares/s!Asuw4D2AHTOZlYc7rk_HkK02f4T2GA/root/content'
    result = requests.get(url)

    df_play = pd.read_csv(StringIO(result.text), sep=';')

    df = df_play.merge(df_conteudo, on='id_conteudo', how='left')
    '''
    , language="python", line_numbers=False)

st.dataframe(df,use_container_width=True,height=256)

st.subheader('Preparação dos dados',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['horas_consumidas'] = df['horas_consumidas'].str.replace(',', '.')
    df['horas_consumidas'] = df['horas_consumidas'].astype(float)
    '''
    , language="python", line_numbers=False)

st.markdown(GetBasicTextMarkdown(20,
'''
Como é possível observar as colunas data e horas_consumidas estão com os tipos de dados \
errados (object), sendo necessário a conversão para o tipo datetime e float respectivamente.''')
,unsafe_allow_html = True)

cols = st.columns([0.5,0.5])
with cols[0]:
    st.table(df.dtypes.astype(str))
    
df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
df['horas_consumidas'] = df['horas_consumidas'].str.replace(',', '.')
df['horas_consumidas'] = df['horas_consumidas'].astype(float)

with cols[1]:
    st.table(df.dtypes.astype(str))


with st.expander('Código',expanded=True):
    st.code(
    '''
    df['conteudo']= df['conteudo'].fillna('desconhecido')
    df['categoria'] = df['categoria'].fillna('desconhecida')
    '''
    , language="python", line_numbers=False)


st.markdown(GetBasicTextMarkdown(20,
'''
Também foram encontrados valores nulos nas colunas conteudo e categoria, isso se deve ao fato do \
conteúdo 10777 não estar registrado na tabela de conteudos, por conta disso iremos preencher os valores nulos \
por <u>\'desconhecido\'</u> e <u>\'desconhecida\'</u> respectivamente.
''')
,unsafe_allow_html = True)

cols = st.columns([0.5,0.5])

with cols[0]:
    st.table(df[df['categoria'].isna()])

df['conteudo']= df['conteudo'].fillna('desconhecido')
df['categoria'] = df['categoria'].fillna('desconhecida')

with cols[1]:
    st.table(df[df['categoria'] == 'desconhecida'])

st.subheader('1 - Quantidade de horas consumidas e plays por categoria',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    df.groupby('categoria').agg(quantidade_horas_consumidas=('horas_consumidas', 'sum'),plays=('conteudo','count')).sort_values(by='quantidade_horas_consumidas', ascending=False).reset_index()
    '''
    , language="python", line_numbers=False)

st.dataframe(df.groupby('categoria').agg(quantidade_horas_consumidas=('horas_consumidas', 'sum'),plays=('conteudo','count')).sort_values(by='quantidade_horas_consumidas', ascending=False).reset_index(),use_container_width=True,hide_index=True)

st.subheader('2 - Ranking de novelas com mais horas consumidas por mês',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    df_novela = df[df['categoria'] == 'novela'].copy()
    df_novela['mes_nome'] = df_novela['data'].dt.strftime('%B')
    df_novela['mes_numero'] = df_novela['data'].dt.month

    df_novela = df_novela.groupby(['categoria','conteudo','mes_nome','mes_numero']).agg({'horas_consumidas': 'sum'}).sort_values(by=['mes_numero', 'horas_consumidas'], ascending=[True, False]).reset_index()
    
    #Novela mais assistida por mês
    df_novela.loc[df_novela.groupby('mes_numero')['horas_consumidas'].idxmax()]
    '''
    , language="python", line_numbers=False)

df_novela = df[df['categoria'] == 'novela'].copy()
df_novela['mes_nome'] = df_novela['data'].dt.strftime('%B')
df_novela['mes_numero'] = df_novela['data'].dt.month

df_novela = df_novela.groupby(['categoria','conteudo','mes_nome','mes_numero']).agg({'horas_consumidas': 'sum'}).sort_values(by=['mes_numero', 'horas_consumidas'], ascending=[True, False]).reset_index()

if st.toggle('Mostrar apenas a novela mais assistida no mês',value=False):
    st.dataframe(df_novela.loc[df_novela.groupby('mes_numero')['horas_consumidas'].idxmax()],use_container_width=True,hide_index=True)
else:
    st.dataframe(df_novela,use_container_width=True,hide_index=True)

st.subheader('3 - Conteúdo de primeiro play do usuário',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    #Solução simples
    df.sort_values('data').groupby('id_user').first().sort_values('data')

    #Solução alternativa/complexa
    df_primeiro_play = pd.DataFrame()

    for user in df['id_user'].unique():
        primeiro_play = df[df['id_user'] == user]['data'].min()
        df_primeiro_play = pd.concat([df_primeiro_play,df[(df['id_user'] == user) & (df['data'] == primeiro_play)]])

    df_primeiro_play.sort_values(by='data',inplace=True)
    df_primeiro_play.reset_index(inplace=True,drop=True)
    '''
    , language="python", line_numbers=False)

st.dataframe(df.sort_values('data').groupby('id_user').first().sort_values('data'),use_container_width=True)

st.subheader('4 - Minutos por play para cada usuário',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    df_minutos_per_play = df.copy()
    df_minutos_per_play['minutos_consumidos'] = df_minutos_per_play['horas_consumidas'] * 60
    df_minutos_per_play = df_minutos_per_play.groupby('id_user').agg({'minutos_consumidos': 'mean'}).sort_values(by='minutos_consumidos', ascending=False).reset_index()
    '''
    , language="python", line_numbers=False)

df_minutos_per_play = df.copy()
df_minutos_per_play['minutos_consumidos'] = df_minutos_per_play['horas_consumidas'] * 60
df_minutos_per_play = df_minutos_per_play.groupby('id_user').agg({'minutos_consumidos': 'mean'}).sort_values(by='minutos_consumidos', ascending=False).reset_index()

st.dataframe(df_minutos_per_play,use_container_width=True,hide_index=True)

st.subheader('5 - Qual a categoria mais consumida para cada usuário',divider=True)

with st.expander('Código',expanded=True):
    st.code(
    '''
    df_categoria_favorita_usuario = df.groupby(['id_user','categoria']).agg({'horas_consumidas': 'sum'}).reset_index().copy()
    df_categoria_favorita_usuario.sort_values(by='horas_consumidas', ascending=False, inplace=True)
    df_categoria_favorita_usuario = df_categoria_favorita_usuario.groupby('id_user').first().reset_index().sort_values(by='horas_consumidas', ascending=False)
    '''
    , language="python", line_numbers=False)

df_categoria_favorita_usuario = df.groupby(['id_user','categoria']).agg({'horas_consumidas': 'sum'}).reset_index().copy()
df_categoria_favorita_usuario.sort_values(by='horas_consumidas', ascending=False, inplace=True)
df_categoria_favorita_usuario = df_categoria_favorita_usuario.groupby('id_user').first().reset_index().sort_values(by='horas_consumidas', ascending=False)

st.dataframe(df_categoria_favorita_usuario,use_container_width=True,hide_index=True)

st.subheader(
    '''
    6 - Conte uma história com os dados! Não precisa ser nada complexo. \
    O objetivo é entendermos como você lida com informações e as analisa.
    ''',divider=True)



title_font_size = 24
legend_title_font_size = 22
legend_font_size = 16
axes_title_font_size = 20
axes_font_size = 18

st.markdown(GetBasicTextMarkdown(18,
'''
A partir dos dados disponíveis foi possível encontrar algumas tendências e padrões interessantes, \
que nos permite inferir algumas teorias para que com mais dados possam ser testadas e validadas. \
'''),unsafe_allow_html = True)

st.divider()

st.markdown(GetBasicTextMarkdown(18,
''' 
O primeiro deles é de que aproximadamente entre agosto e outubro há uma queda acentuada nas horas \
consumidas enquanto que em novembro há um aumento abrupto, evidênciado pelos gráficos abaixo. \
'''),unsafe_allow_html = True)

df = df.sort_values('data')

cols = st.columns([0.5,0.5])
with cols[0]:
    fig = px.line(df, x='data', y='horas_consumidas',color='categoria',
    color_discrete_map={'novela': 'Crimson', 'serie': 'DeepSkyBlue','desconhecida':'GreenYellow'},symbol="categoria",
    title='Horas consumidas por mês')

    fig.update_xaxes(title='Mês', title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))
    fig.update_yaxes(title='Horas Consumidas',title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))

    fig.update_layout(
        title=dict(
            font=dict(
                size=title_font_size,
            ),
        ),
        legend=dict(
            title_font_size=legend_title_font_size,
            font=dict(
                size=legend_font_size,
            ),
        ),
    )

    st.plotly_chart(fig,use_container_width=True)

with cols[1]:
    df['mes_numero'] = df['data'].dt.month
    df_horas_mes = df.copy().groupby(['mes_numero']).agg({'horas_consumidas': 'sum'}).reset_index().sort_values(by='mes_numero', ascending=True)
    
    fig = px.line(df_horas_mes, x='mes_numero', y='horas_consumidas', title='Horas totais consumidas por mês')

    fig.update_xaxes(title='Mês', title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))
    fig.update_yaxes(title='Horas Consumidas',title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))

    fig.update_traces(line=dict(color='Gold'))

    fig.update_layout(
        title=dict(
            font=dict(
                size=title_font_size,
            ),
        ),
        legend=dict(
            title_font_size=legend_title_font_size,
            font=dict(
                size=legend_font_size,
            ),
        ),
    )

    fig.update_xaxes(range=[df_horas_mes['mes_numero'].min() - 0.25, df_horas_mes['mes_numero'].max() + 0.25])
    fig.update_xaxes(
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    )
    st.plotly_chart(fig,use_container_width=True)
    #st.markdown(GetBasicTextMarkdown(20,'''Quantidade de horas consumidas totais por mês'''),unsafe_allow_html = True)
    #st.table(df_horas_mes)

st.markdown(GetBasicTextMarkdown(18,
'''
Tal comportamento aparenta ter alguma relação com períodos típicos de férias, o que \
faz sentido pois os usuários teriam mais tempo disponível para lazer e entreterimento. \
Considerando esse padrão de consumo, é recomendável que os servidores estejam dimensionados para \
suportar o aumento de tráfego no final do ano e aproveitar os meses de menor consumo para manutenções.
'''),unsafe_allow_html = True)

st.divider()

st.markdown(GetBasicTextMarkdown(18,
'''
O segundo padrão interessante é de que a maioria dos usuários tiveram a seu primeiro play com novelas, provavelmente \
movidos pelo desejo de ver algum capítulo que não conseguiram assistir no horário de exibição, contudo, \
eles passaram a consumir mais séries do que novelas na plataforma, indicando que as séries desempenham grande papel \
na retenção de usuários. Afirmação reforçada pelo fato de que a maioria dos usuários assistiram mais horas de séries do que \
qualquer outra categoria.
'''),unsafe_allow_html = True)

fig = px.bar(df, x='data', y='horas_consumidas', color='categoria', barmode='group', facet_col='id_user',
color_discrete_map={'novela': 'Crimson', 'serie': 'DeepSkyBlue','desconhecida':'GreenYellow'})
st.plotly_chart(fig,use_container_width=True)

st.markdown(GetBasicTextMarkdown(18,
'''
Afirmação reforçada pelo fato de que a maioria dos usuários assistiram mais horas de séries do que \
qualquer outra categoria.
'''),unsafe_allow_html = True)

st.dataframe(df_categoria_favorita_usuario,use_container_width=True,hide_index=True)

st.divider()

st.markdown(GetBasicTextMarkdown(18,
'''
E por fim, a série D teve uma queda atípica se comparado com a tendência de horas de consumo, a sua queda \
de horas consumidas é menos abrupta do que dos demais conteúdos, porém, não há um aumento de consumo \
posteriormente, como ocorre com as demais séries. Isso pode indicar que a série D consegue manter a sua base de \
usuários, mas não consegue atrair novos usuários.
'''),unsafe_allow_html = True)


fig = px.line(df, x='data', y='horas_consumidas', title='Horas totais consumidas por mês',color='conteudo',
color_discrete_map={'A': 'HoneyDew', 'B': 'Ivory','C':'GhostWhite','D':'DeepSkyBlue','desconhecido':'Gainsboro'})


fig.update_xaxes(title='Data', title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))
fig.update_yaxes(title='Horas Consumidas',title_font=dict(size=axes_title_font_size), tickfont=dict(size=axes_font_size))

fig.update_layout(
    title=dict(
        font=dict(
            size=title_font_size,
        ),
    ),
    legend=dict(
        title_font_size=legend_title_font_size,
        font=dict(
            size=legend_font_size,
        ),
    ),
)

st.plotly_chart(fig,use_container_width=True)
