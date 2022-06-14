from flask import Flask, redirect, render_template, request, session, flash, url_for
import json
import requests
import sys
import hmac, hashlib, base64
import os
import zipfile as zip
import psycopg2 as pg
import psycopg2.extras
from datetime import date, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "efjfuidufeuwhduhfrgi"

url = "https://0xfukg7u78.execute-api.us-east-1.amazonaws.com/v1"

isLogged = False


def createTableContato():
    sql = """CREATE TABLE tb_contato(
        id serial,
        tag varchar(30),
        value varchar(50),
        link varchar(80),
        constraint pk_tb_contato_id primary key (id)
    );"""
    return sql

def createTableProgramacao():
    sql = """CREATE TABLE tb_programacao(
        diadasemana varchar(15),
        inicio varchar(30),
        fim varchar(50),
        nome varchar(80),
        descricao varchar(200),
        constraint pk_tb_programacao_id primary key (diadasemana, inicio)
    );"""
    return sql

def createTablePromocao():
    sql = """CREATE TABLE tb_promocao(
        id serial,
        titulo varchar(90),
        descricao varchar(250),
        premio varchar(50),
        requisitos varchar(200),
        link varchar(100),
        inicio varchar(15),
        termino varchar(15),
        constraint pk_tb_promocao_id primary key (id)
    );"""
    return sql

def dropTable (nome):
    sql = f"""
    drop table {nome};
    """
    return sql

def getAll(nome):
    sql = f"""
    select * from {nome};
    """
    return sql

def getWeekday(day):
    sql = f"""
    select * from tb_programacao
    where diadasemana = '{day}';
    """
    return sql

def getElementByID(nome, id):
    sql = f"""
    select * from {nome} where id = {id};
    """
    return sql

def deleteContent(nome, id):
    sql = f"""
    delete from {nome} where id = {id} 
    """
    return sql

try:
    con = pg.connect(
        database = 'db_painel',
        user = 'postgres',
        password = 'admin',
        host = '127.0.0.1',
        port = '5432'
    )

    print("Conexão realizada com sucesso")

    # sql = createTableProgramacao()
    # sql2 = createTableContato()
    # sql = createTablePromocao()

    cur = con.cursor()

    # cur.execute(cur.mogrify(sql))
    # cur.execute(cur.mogrify(sql2))
    # con.commit()

except Exception as erro:
    print(f'Erro na conexão com o banco de dados: {erro}')

def getUrl(comp):
    erro = False
    try:
        res = requests.get(f"{url}{comp}")
    except:
        erro = True
        print(erro)    
    
    if(res.status_code != 200):
        erro = True
        data = res
    else:
        data = res.json()   
    
    print(data)
    return data, erro
    
def secretGen(username):
    clientID = '3dh2092l64flp39rql62ocgl6o'
    clientSecret = '1o06f8lt556opisctur8a79sgqk5vabb8bqplplph2kjh5tt7vlm'
    message = bytes(username+clientID,'utf-8')
    key = bytes(clientSecret,'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()

    print("SECRET HASH:",secret_hash)

    return secret_hash

# rota inicial
@app.route("/")
def home():    
    global isLogged
    if(isLogged):
        data = getUrl("/tennant")
        return render_template("home.html", 
        data = data)
    else:
        return redirect('/login')

# rota login
@app.route("/login", methods = ["POST", "GET"])
def login():
    erro = False
    data = None
    global isLogged
    if(request.method == 'POST'):
        hash = secretGen( request.form["email"])

        corpo = {
            "user": request.form["email"],
            "pass":  request.form["password"],
            "secret": hash
        }

        headers = {"Content-Type": "application/json"}

        res = requests.post(f"https://0xfukg7u78.execute-api.us-east-1.amazonaws.com/dev/auth/login", json=corpo, headers=headers)
        print(res.status_code)
        
        if(res.status_code != 200):
            erro = True
            # error = 'Email ou senha incorretos, tente novamente'
            data = res 
            return render_template("login.html",
            data = data, erro = True) 
        else:
            data = res.json()
            erro = False
            isLogged = True
            print(f"Está logado e: {isLogged}")
            return redirect('/')

    return render_template("login.html",
    data = data, erro = erro)

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")



# rota Programação
@app.route("/programacao", methods = ["GET", "POST"])
def programacao():
    dia_da_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    weekday = []
    try:
        sql = getWeekday("segunda")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("terca")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("quarta")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("quinta")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("sexta")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("sabado")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        sql = getWeekday("domingo")
        cur.execute(cur.mogrify(sql))
        weekday.append(cur.fetchall())

        print(weekday)
        print(weekday[2])

    except Exception as e:
        print(e)
 

    return render_template("programacao.html", weekday = weekday, dia_da_semana = dia_da_semana)

# rota cadastro Programação
@app.route("/cadastro_programacao", methods = ["GET", "POST"])
def cadastro_programacao():
    
    if(request.method == 'POST'):
        inicio = request.form["inicioprogramacao"]
        termino = request.form["terminoprogramacao"]
        titulo = request.form["tituloprogramacao"]
        descricao = request.form["descricaoprogramacao"]

        dia = request.form.getlist('dia')    
        print(request.form.getlist('dia'))


        for i in range(len(dia)):
            sql = f"""
            insert into tb_programacao(diadasemana, inicio, fim, nome, descricao)
            values ('{dia[i]}', '{inicio}', '{termino}', '{titulo}', '{descricao}');
            """
            cur.execute(cur.mogrify(sql))
            
            # flash("Contato inserido com sucesso")
        con.commit()
        return redirect("/programacao")
        

    return render_template("cadastro/cadastro_programacao.html")

@app.route("/editar_programacao/<dia>/<inicio>", methods = ["GET", "POST"])
def editar_programacao(dia, inicio):
    if(request.method == 'POST'):
        novoinicio = request.form["inicioprogramacao"]
        termino = request.form["terminoprogramacao"]
        titulo = request.form["tituloprogramacao"]
        descricao = request.form["descricaoprogramacao"]        
        try:

            sql = f"""
                update tb_programacao set
                    diadasemana = '{dia}',
                    inicio = '{novoinicio}',
                    fim = '{termino}',
                    nome = '{titulo}',
                    descricao = '{descricao}'
                    where diadasemana = '{dia}' and inicio = '{inicio}'
                """
            cur.execute(cur.mogrify(sql))

            con.commit()
        except Exception as error:
            print(error)

        return redirect("/programacao")

    try:
        sql = f"""
            select * from tb_programacao where
            diadasemana = '{dia}' and inicio = '{inicio}';
        """
        cur.execute(cur.mogrify(sql))
    except Exception as erro:
        print(f"{erro}")

    linhas = cur.fetchall()
    
    return render_template("editar/editar_programacao.html",
    linhas = linhas[0])

@app.route("/deletar_programacao/<dia>/<inicio>", methods = ["GET", "POST"])
def deletar_programacao(dia, inicio):
    sql = f"""
    delete from tb_programacao where diadasemana = '{dia}' and  inicio = '{inicio}';
    """
    try:
        cur.execute(cur.mogrify(sql))
        con.commit()
        # flash("Contato deletado com sucesso")
        print("deletado com sucesso")
        return redirect("/programacao")
    except Exception as erro:
        print(f"Erro: {erro}")
        # flash(f"Ocorreu um erro, tente novamente {erro}")
        return  redirect("/programacao")

# rota contato
@app.route("/contato", methods = ["GET", "POST"])
def contato():    
    try:
        sql = getAll("tb_contato")
        cur.execute(cur.mogrify(sql))
    except Exception as erro:
        print(f"{erro}")

    linhas = cur.fetchall()
        
    return render_template("contato.html",
    linhas = linhas)

# rota cadastrar contato
@app.route("/cadastro_contato", methods = ["GET", "POST"])
def cadastro_contato():
    if(request.method == 'POST'):
        rede = request.form["redesocial"]
        usuario = request.form["usuario"]
        link = request.form["linkcontato"]

        sql = f"""
        insert into tb_contato(tag, value, link)
        values ('{rede}', '{usuario}', '{link}');
        """

        try:
            cur.execute(cur.mogrify(sql))
            con.commit()
            # flash("Contato inserido com sucesso")
            return redirect("/contato")
        except Exception as erro:
            print(f"Erro: {erro}")
            # flash(f"Ocorreu um erro, tente novamente {erro}")
        return  redirect("/cadastro_contato")
    return render_template("cadastro/cadastro_contato.html")

# rota editar contato
@app.route("/editar_contato/<id>", methods = ["GET", "POST"])
def editar_contato(id):
    if(request.method == 'POST'):
        rede = request.form["redesocial"]
        usuario = request.form["usuario"]
        link = request.form["linkcontato"]

        sql = f"""
        update tb_contato set
        tag = '{rede}',
        value = '{usuario}',
        link = '{link}'
        where id = {id}
        """

        try:
            cur.execute(cur.mogrify(sql))
            con.commit()
            return redirect("/contato")
        except Exception as erro:
            print(f"Erro: {erro}")
            flash(f"Ocorreu um erro: {erro}")
            redirect("/editar_contato")
        return  redirect("/editar_contato")

    try:
        sql = getElementByID("tb_contato", id)
        cur.execute(cur.mogrify(sql))
    except Exception as erro:
        print(f"{erro}")

    linhas = cur.fetchall()
    
    return render_template("editar/editar_contato.html",
    linhas = linhas[0])

# rota deletar contato
@app.route("/deletar_contato/<id>", methods = ["GET", "POST"])
def deletar_contato(id):
    sql = deleteContent("tb_contato", id)
    try:
        cur.execute(cur.mogrify(sql))
        con.commit()
        # flash("Contato deletado com sucesso")
        print("deletado com sucesso")
        return redirect("/contato")
    except Exception as erro:
        print(f"Erro: {erro}")
        # flash(f"Ocorreu um erro, tente novamente {erro}")
        return  redirect("/contato")

# rota promoção
@app.route("/promocao")
def promocao():    
    try:
        sql = getAll("tb_promocao")
        cur.execute(cur.mogrify(sql))
    except Exception as erro:
        print(f"{erro}")

    linhas = cur.fetchall()
        
    return render_template("promocao.html",
    linhas = linhas)

# rota cadastrar promocao
@app.route("/cadastro_promocao", methods = ["GET", "POST"])
def cadastro_promocao():
    if(request.method == 'POST'):
        titulo = request.form["titulopromo"]
        descricao = request.form["descricaopromo"]
        premio = request.form["premiopromo"]
        requisitos = request.form["requisitospromo"]
        link = request.form["linkpromo"]
        inicio = request.form["iniciopromo"]
        termino = request.form["terminopromo"]
        
        termino = datetime.strptime(termino, '%Y-%m-%d').date()
        inicio = datetime.strptime(inicio, '%Y-%m-%d').date()
        inicio = inicio.strftime('%d/%m/%Y')
        termino = termino.strftime('%d/%m/%Y')

        sql = f"""
        insert into tb_promocao(titulo, descricao, premio, requisitos, link, inicio, termino)
        values ('{titulo}', '{descricao}', '{premio}', '{requisitos}', '{link}', '{inicio}', '{termino}');
        """

        try:
            cur.execute(cur.mogrify(sql))
            con.commit()
            # flash("Contato inserido com sucesso")
            return redirect("/promocao")
        except Exception as erro:
            print(f"Erro: {erro}")
            # flash(f"Ocorreu um erro, tente novamente {erro}")
        return  redirect("/cadastro_contato")
    return render_template("cadastro/cadastro_promocao.html")

# rota editar promocao
@app.route("/editar_promocao/<id>", methods = ["GET", "POST"])
def editar_promocao(id):
    if(request.method == 'POST'):
        titulo = request.form["titulopromo"]
        descricao = request.form["descricaopromo"]
        premio = request.form["premiopromo"]
        requisitos = request.form["requisitospromo"]
        link = request.form["linkpromo"]
        inicio = request.form["iniciopromo"]
        termino = request.form["terminopromo"]

        sql = f"""
        update tb_promocao set
        titulo = '{titulo}',
        descricao = '{descricao}',
        premio = '{premio}',
        requisitos = '{requisitos}',
        link = '{link}',
        inicio = '{inicio}',
        termino = '{termino}'
        where id = {id};
        """

        try:
            cur.execute(cur.mogrify(sql))
            con.commit()
            return redirect("/promocao")
        except Exception as erro:
            print(f"Erro: {erro}")
            flash(f"Ocorreu um erro: {erro}")
            redirect("/editar_promocao")
        return  redirect("/editar_promocao")

    try:
        sql = getElementByID("tb_promocao", id)
        cur.execute(cur.mogrify(sql))
    except Exception as erro:
        print(f"{erro}")

    linha = cur.fetchall()
    
    return render_template("editar/editar_promocao.html",
    linha = linha[0])

# rota deletar promocao
@app.route("/deletar_promocao/<id>", methods = ["GET", "POST"])
def deletar_promocao(id):
    sql = deleteContent("tb_promocao", id)
    try:
        cur.execute(cur.mogrify(sql))
        con.commit()
        # flash("Contato deletado com sucesso")
        print("deletado com sucesso")
    except Exception as erro:
        print(f"Erro: {erro}")
        # flash(f"Ocorreu um erro, tente novamente {erro}")
    return  redirect("/promocao")


@app.route("/ziparJson")
def zipar_json():

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = getAll("tb_contato")
    cur.execute(cur.mogrify(sql))
    contato = cur.fetchall()
    sql = getAll("tb_programacao")
    cur.execute(cur.mogrify(sql))
    programacao = cur.fetchall()
    sql = getAll("tb_promocao")
    cur.execute(cur.mogrify(sql))
    promocao = cur.fetchall()
    
    contato1 = []
    programacao1 = []
    promocao1 = []

    for row in contato:
        contato1.append(dict(row))

    for row in programacao:
        programacao1.append(dict(row))

    for row in promocao:
        promocao1.append(dict(row))

    f = open("data/output.json", "w")
    json.dump([contato1, programacao1, promocao1], f, sort_keys=True, indent=4)
    f.close()

    path_zip = os.path.join(r"E:\Drive\projetos\Python\painel\data\output.zip")
    path_dir = os.path.join("E:\\Drive\\projetos\\Python\\painel\\data\\output.json")

    zf = zip.ZipFile(path_zip, "w")

    zf.write(path_dir)
    zf.close()

    return  redirect("/")


if __name__ == "__main__":
        app.run(debug=True)


