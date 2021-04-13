from psycopg2 import connect, ProgrammingError, OperationalError
from psycopg2.extras import RealDictCursor
from flask import Flask, request, render_template, redirect
from datetime import date

app = Flask(__name__)

U = "postgres"
P = "coderslab"
H = "localhost"
DB = "library_db"


@app.route("/books", methods=['GET', 'POST'])
def booklist():
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT book.id, isbn, book.name, author.name AS auth_name "
                           "FROM book JOIN author ON book.author_id=author.id")
            operation = cursor.fetchall()
        cnx.close()
        html = """ <table>
               <tr> 
               <th>id</th>
               <th>Author</th>
               <th>Name</th>
               <th>ISBN</th>
               </tr>
               """
        for book_record in operation:
            html += render_template("form.html", book=book_record)
        html += "</table>"
        segue_to_addbook = f"""<form action="/add_book" method="GET">
                    <button type="submit">Add book</button></form>"""
        segue_to_bookdetails = f"""<form action="/books" method="POST">
                                <button type="submit">Show book details</button>
                                <label>book id: <input type="number" name="id_of_book"></label></form>
                                """
        segue_to_bookdeletion = f"""<form action="/books" method="POST">
                                        <button type="submit">Delete book</button>
                                        <label>book id: <input type="number" name="id_of_book2"></label></form>
                                        """
        segue_to_clients = """<form action="/clients" method="GET">
                            <button type="submit">Go to clients</button></form>"""
        segue_to_loan = """<form action="/loan" method="GET">
                                    <button type="submit">Go to loan page</button></form>"""

        return segue_to_addbook + segue_to_bookdetails + segue_to_bookdeletion + \
               segue_to_clients + segue_to_loan + "<Br><Br>" + html
    else:
        idbook = int(request.form.get("id_of_book", 0))
        idbook2 = int(request.form.get("id_of_book2", 0))
        if idbook2 == 0:
            return redirect(f"/book_details/{idbook}")
        elif idbook == 0:
            return redirect(f"/delete_book/{idbook2}")



@app.route("/add_book", methods=['GET', 'POST'])
def book_adding():
    if request.method == 'GET':
        add_form = f"""
        <form action="/add_book" method="POST">
            <label>
            Input ISBN:
                <input type="number" name="isbn">
            </label>
            <label>
            Input author:
                <input type="text" name="author">
            </label>
            <label>
            Input title:
                <input type="text" name="name">
            </label>
            <label>
            Input description:
                <input type="text" name="description">
            </label>
            <button type="submit">Add record to database</button>
        </form>
        """
        segue_to_homepage = f"""<form action="/books" method="GET">
                                    <button type="submit">Return to books</button></form>"""
        return add_form + segue_to_homepage
    else:
        book_isbn = int(request.form["isbn"])
        book_name = str(request.form["name"])
        book_desc = str(request.form["description"])
        book_author = str(request.form["author"])

        conn = connect(user=U, password=P, host=H, database=DB)

        with conn.cursor() as curs:
            conn.autocommit = True
            curs.execute(
                f"INSERT INTO book(isbn, name, description) VALUES ({book_isbn}, '{book_name}', '{book_desc}')")
            try:
                curs.execute(f"SELECT id FROM author WHERE name = '{book_author}'")
                res = int(curs.fetchone()[0])
                curs.execute(f"UPDATE book SET author_id = {res} WHERE author_id is null")
            except TypeError:
                curs.execute(f"INSERT INTO author(name) VALUES ('{book_author}')")
                curs.execute(f"UPDATE book SET author_id = (SELECT id FROM author WHERE name = '{book_author}') "
                             f"WHERE author_id is null")
        conn.close()

        segue_to_homepage = f"""<form action="/books" method="GET">
                            <button type="submit">Return to books</button></form>"""

        return "Book added." + "<Br><Br>" + segue_to_homepage


@app.route("/book_details/<int:bookid>", methods=['GET', 'POST'])
def book_details(bookid):
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT book.id, isbn, description, is_loaned, book.name, author.name AS auth_name "
                           f"FROM book JOIN author ON book.author_id=author.id WHERE book.id={bookid}")
            operation = cursor.fetchone()
        cnx.close()
        if operation['is_loaned'] is False:
            loaned = "Not loaned"
        else:
            loaned = "Loaned"
        detail_form = f"""<table style="width:60%">
                       <tr>
                       <th>id</th>
                       <th>Author</th>
                       <th>Name</th>
                       <th>Description</th>
                       <th>ISBN</th>
                       <th>Status</th>
                       </tr>
                       {render_template("book_details_id.html", book=operation)}
                       <td align="center">{loaned}</td></tr>
                       </table>
                       """

        segue_to_homepage = f"""<form action="/books" method="GET">
                                    <button type="submit">Return to books</button></form>"""
        segue_to_bookdeletion = f"""<form action="/book_details/{bookid}" method="POST">
                                    <button type="submit">Delete book</button></form>"""
        return detail_form + "<Br><Br>" + segue_to_homepage + segue_to_bookdeletion
    else:
        return redirect(f"/delete_book/{bookid}")


@app.route("/delete_book/<int:bookid>", methods=['GET', 'POST'])
def delete_book(bookid):
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor() as cursor:
            cnx.autocommit = True
            cursor.execute(f"SELECT book_id FROM clients_book WHERE book_id={bookid}")
            if cursor.fetchone() is None:
                cursor.execute(f"DELETE FROM book WHERE id={bookid}")
            else:
                cursor.execute(f"DELETE FROM clients_book WHERE book_id={bookid}")
                cursor.execute(f"DELETE FROM book WHERE id={bookid}")
        cnx.close()
        segue_to_homepage = f"""<form action="/books" method="GET">
                                            <button type="submit">Return to books</button></form>"""
        return "Book has been removed from database." + "<Br><Br>" + segue_to_homepage
    else:
        return None


@app.route("/clients", methods=['GET', 'POST'])
def clients():
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, first_name, last_name FROM client")
            operation = cursor.fetchall()
        cnx.close()
        html = """ <table>
               <tr> 
               <th style="padding:10px">id</th>
               <th style="padding:10px">First Name</th>
               <th style="padding:10px">Last Name</th>
               </tr>
               """
        for client_record in operation:
            html += render_template("clients_template.html", client=client_record)
        html += "</table>"
        segue_to_homepage = f"""<form action="/books" method="GET">
                                                    <button type="submit">Return to books</button></form>"""
        segue_to_addclient = f"""<form action="/add_client" method="GET">
                                    <button type="submit">Add client</button></form>"""
        segue_to_clientdetails = """<form action="/clients" method="POST">
                                                        <button type="submit">Show client details</button>
                                                        <label>client id: <input type="number" name="id_of_client">
                                                        </label></form>
                                                        """
        segue_to_clientdeletion = """<form action="/clients" method="POST">
                                                    <button type="submit">Delete client</button>
                                                    <label>client id: <input type="number" name="id_of_client2">
                                                    </label></form>
                                                    """
        return segue_to_homepage + segue_to_addclient + segue_to_clientdetails + segue_to_clientdeletion + html
    else:
        idclient = int(request.form.get("id_of_client", 0))
        idclient2 = int(request.form.get("id_of_client2", 0))
        if idclient2 == 0:
            return redirect(f"/client_details/{idclient}")
        elif idclient == 0:
            return redirect(f"/delete_client/{idclient2}")


@app.route("/add_client", methods=['GET', 'POST'])
def add_client():
    if request.method == 'GET':
        add_form = f"""
        <form action="/add_client" method="POST">
            <label>
            Input First Name: 
                <input type="text" name="firstname">
            </label>
            <label>
            Input Last Name: 
                <input type="text" name="lastname">
            </label>
            <button type="submit">Add record to database</button>
        </form>
        """
        segue_to_client = f"""<form action="/clients" method="GET">
                                    <button type="submit">Return to clients</button></form>"""
        return add_form + segue_to_client
    else:
        first_name = str(request.form["firstname"])
        last_name = str(request.form["lastname"])

        conn = connect(user=U, password=P, host=H, database=DB)

        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            conn.autocommit = True
            curs.execute("INSERT INTO client(first_name, last_name) "
                         f"VALUES ('{first_name}', '{last_name}') RETURNING first_name, last_name")
            operation = curs.fetchone()
        conn.close()

        segue_to_client = f"""<form action="/clients" method="GET">
                            <button type="submit">Return to clients</button></form>"""

        return f"Client added: {operation['first_name']} {operation['last_name']}." + "<Br><Br>" + segue_to_client


@app.route("/delete_client/<int:clientid>", methods=['GET', 'POST'])
def delete_client(clientid):
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor() as cursor:
            cnx.autocommit = True
            cursor.execute(f"SELECT client_id FROM clients_book WHERE client_id={clientid}")
            if cursor.fetchone() is None:
                cursor.execute(f"DELETE FROM client WHERE id={clientid}")
            else:
                cursor.execute(f"DELETE FROM clients_book WHERE client_id={clientid}")
                cursor.execute(f"DELETE FROM client WHERE id={clientid}")
        cnx.close()
        segue_to_client = f"""<form action="/clients" method="GET">
                                   <button type="submit">Return to clients</button></form>"""
        return "Client has been removed from database." + "<Br><Br>" + segue_to_client
    else:
        return None


@app.route("/client_details/<int:clientid>", methods=['GET', 'POST'])
def client_details(clientid):
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT client.id, first_name, last_name, book.name, is_loaned, loan_date, return_date "
                           "FROM client LEFT JOIN clients_book ON client.id=clients_book.client_id "
                          f"LEFT JOIN book ON book.id=clients_book.book_id WHERE client.id={clientid}")
            operation = cursor.fetchall()
        cnx.close()
        detail_form = f"""<table style="width:60%">
                       <tr>
                       <th>client id</th>
                       <th>First Name</th>
                       <th>Last Name</th>
                       <th>Book Title</th>
                       <th>Loan Date</th>
                       <th>Return Date</th>
                       <th>Loaned By Client</th>
                       </tr>      
                       """
        for client_record in operation:
            detail_form += render_template("client_details_id.html", client=client_record)
            if client_record['is_loaned'] is False:
                loaned = "Returned"
            else:
                loaned = "Loaned"
            detail_form += f"<td align='center'>{loaned}</td></tr>"
        detail_form += "</table>"
        segue_to_client = f"""<form action="/clients" method="GET">
                                           <button type="submit">Return to clients</button></form>"""
        segue_to_clientdeletion = f"""<form action="/client_details/{clientid}" method="POST">
                                    <button type="submit">Delete client</button></form>"""
        return detail_form + "<Br><Br>" + segue_to_client + segue_to_clientdeletion
    else:
        return redirect(f"/delete_client/{clientid}")


@app.route("/loan", methods=['GET', 'POST'])
def loan():
    if request.method == 'GET':
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT book.id, name, description, is_loaned, client.first_name, client.last_name, "
                           "loan_date, return_date FROM book LEFT JOIN clients_book ON book.id=clients_book.book_id "
                           "LEFT JOIN client ON client.id=clients_book.client_id;")
            operation = cursor.fetchall()
        cnx.close()
        detail_form = f"""<table style="width:60%">
                               <tr>
                               <th>book id</th>
                               <th>Title</th>
                               <th>Description</th>
                               <th>First Name</th>
                               <th>Last Name</th>
                               <th>Loan Date</th>
                               <th>Return Date</th>
                               <th>Loan Status</th>
                               </tr>      
                               """
        for book_record in operation:
            if book_record['first_name'] is None:
                book_record['first_name'] = " "
            if book_record['last_name'] is None:
                book_record['last_name'] = " "
            if book_record['loan_date'] is None:
                book_record['loan_date'] = " "
            if book_record['return_date'] is None:
                book_record['return_date'] = " "
            detail_form += render_template("book_records.html", book=book_record)
            if book_record['is_loaned'] is False:
                loaned = "Free"
            else:
                loaned = "Loaned"
            detail_form += f"<td align='center'>{loaned}</td></tr>"
        detail_form += "</table>"
        loan_a_book = f"""<form action="/loan" method="POST">
                                    <label>Client name: <input type="text" name="clientname"></label>
                                    <label>Book name: <input type="text" name="bookname"></label>
                                    <button type="submit">Loan a book</button></form>"""
        segue_to_homepage = f"""<form action="/books" method="GET">
                                <button type="submit">Return to books</button></form>"""
        return loan_a_book + segue_to_homepage + detail_form
    else:
        clientname = str(request.form["clientname"])
        bookname = str(request.form["bookname"])
        today = date.today().isoformat()
        split_clientname = clientname.split(sep=" ")
        firstname = split_clientname[0]
        lastname = split_clientname[1]
        cnx = connect(user=U, password=P, host=H, database=DB)
        with cnx.cursor() as cursor:
            cnx.autocommit = True
            cursor.execute(f"SELECT id FROM book WHERE name='{bookname}'")
            book_id = cursor.fetchone()[0]
            cursor.execute(f"SELECT id FROM client WHERE first_name = '{firstname}' AND last_name = '{lastname}'")
            client_id = cursor.fetchone()[0]
            cursor.execute(f"INSERT INTO clients_book(book_id, client_id, loan_date) "
                           f"VALUES ({book_id}, {client_id}, '{today}')")
            cursor.execute(f"UPDATE book SET is_loaned = True WHERE id = {book_id}")
        cnx.close()
        segue_to_homepage = f"""<form action="/books" method="GET">
                                        <button type="submit">Return to books</button></form>"""
        segue_to_loanpage = f"""<form action="/loan" method="GET">
                                                <button type="submit">Return to loan page</button></form>"""
        return f"Book {bookname} is now loaned by {clientname}." + segue_to_loanpage + segue_to_homepage


app.run(debug=True)
