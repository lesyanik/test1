from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Tables


class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)

    orders = db.relationship('Order', backref='client')

    def __repr__(self):
        return '<Client %r' % self.client_id


class Auto(db.Model):
    auto_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    price = db.Column(db.Float, nullable=False)
    code = db.Column(db.String(11), unique=True, nullable=False)
    manufacturer = db.Column(db.String(70), nullable=False)

    orders = db.relationship('Order', backref='auto')
    order_entries = db.relationship('OrderEntry', backref='auto')
    sale_entries = db.relationship('SaleEntry', backref='auto')

    def __repr__(self):
        return '<Auto %r' % self.auto_id


class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.auto_id'), nullable=False)

    order_entries = db.relationship('OrderEntry', backref='order')
    sales = db.relationship('Sale', backref='order')

    def __repr__(self):
        return '<Order %r' % self.order_id


class Sale(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    sale_cost = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.utcnow())

    sale_entries = db.relationship('SaleEntry', backref='sale')

    def __repr__(self):
        return '<Sale %r' % self.sale_id


class OrderEntry(db.Model):
    order_entry_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.order_id'), nullable=False)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.auto_id'), nullable=False)

    def __repr__(self):
        return '<OrderEntry %r' % self.order_entry_id


class SaleEntry(db.Model):
    sale_entry_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.sale_id'), nullable=False)
    auto_id = db.Column(db.Integer, db.ForeignKey('auto.auto_id'), nullable=False)

    def __repr__(self):
        return '<SaleEntry %r' % self.sale_entry_id


# Main Page


@app.route('/')
@app.route('/home')
def hello_world():
    return render_template("index.html")


# Clients Pages


@app.route('/create-client', methods=['POST', 'GET'])
def client_create():
    if request.method == "POST":
        client_name = request.form['client_name']
        client_name = client_name.strip()

        client_phone = request.form['client_phone']
        if not client_phone.isnumeric():
            return redirect(url_for('error_page', msg="Не удалось добавить клиента, так как номера телефона указан неверно."))
        client_code = request.form['client_code']
        if not client_code.isnumeric():
            return redirect(url_for('error_page', msg="Не удалось добавить клиента, так как код указан неверно."))

        new_client = Client(name=client_name, phone=client_phone, code=client_code)

        try:
            db.session.add(new_client)
            db.session.commit()
            return redirect('/clients-list')
        except:
            return "Error happened"
    else:
        return render_template("create-client.html")


@app.route('/clients-list')
def clients_list():
    clients = Client.query.order_by(Client.client_id).all()
    return render_template("clients-list.html", clients=clients)


@app.route('/clients-list/<int:client_id>/change', methods=['POST', 'GET'])
def client_change_information(client_id):
    client = Client.query.get(client_id)
    if request.method == "POST":
        client.name = request.form['client_name']
        client.phone = request.form['client_phone']
        client.code = request.form['client_code']

        if not client.phone.isnumeric():
            return redirect(url_for('error_page', msg="Не удалось изменить данные клиента, так как номера телефона указан неверно."))
        if not client.code.isnumeric():
            return redirect(url_for('error_page', msg="Не удалось изменить данные клиента, так как код указан неверно."))
        try:
            db.session.commit()
            return redirect('/clients-list')
        except:
            return "Error happened"
    else:
        return render_template("client-information.html", client=client)


@app.route('/clients-list/<int:client_id>/delete')
def client_delete(client_id):
    client = Client.query.get_or_404(client_id)
    orders = Order.query.filter_by(client_id=client_id).all()
    if len(orders) > 0:
        msg = "Невозможно удалить клиента, так как с ним существуют заказы: "
        for order in orders:
            msg += "№" + str(order.order_id) + ", "
        return redirect(url_for('error_page', msg=msg))
    try:
        db.session.delete(client)
        db.session.commit()
        return redirect('/clients-list')
    except:
        return "Error happened"


# Cars Pages


@app.route('/create-auto', methods=['POST', 'GET'])
def auto_create():
    if request.method == "POST":
        auto_name = request.form['auto_name']
        if not auto_name or not auto_name.strip():
            return redirect(url_for('error_page', msg="Не удалось добавить авто, так как указано пустое название."))
        auto_price = request.form['auto_price']
        if not auto_price.isnumeric():
            return redirect(url_for('error_page', msg="Не удалось добавить авто, так как цена указана неверно."))
        auto_code = request.form['auto_code']
        if not auto_code or not auto_code.strip():
            return redirect(url_for('error_page', msg="Не удалось добавить авто, так как указан пустой код."))
        auto_manufacturer = request.form['auto_manufacturer']
        if not auto_manufacturer or not auto_manufacturer.strip():
            return redirect(url_for('error_page', msg="Не удалось добавить авто, так как указано пустое название производителя."))

        new_auto = Auto(name=auto_name, price=auto_price, code=auto_code, manufacturer=auto_manufacturer)

        try:
            db.session.add(new_auto)
            db.session.commit()
            return redirect('/autos-list')
        except:
            return "Error happened"
    else:
        return render_template("create-auto.html")


@app.route('/autos-list')
def autos_list():
    autos = Auto.query.order_by(Auto.auto_id).all()
    return render_template("autos-list.html", autos=autos)


@app.route('/autos-list/<int:auto_id>/change', methods=['POST', 'GET'])
def auto_change_information(auto_id):
    auto = Auto.query.get(auto_id)
    if request.method == "POST":
        auto.name = request.form['auto_name']
        auto.price = request.form['auto_price']
        auto.code = request.form['auto_code']
        auto.manufacturer = request.form['auto_manufacturer']

        try:
            db.session.commit()
            return redirect('/autos-list')
        except:
            return "Error happened"
    else:
        return render_template("auto-information.html", auto=auto)


@app.route('/autos-list/<int:auto_id>/delete')
def auto_delete(auto_id):
    auto = Auto.query.get_or_404(auto_id)
    orders = Order.query.filter_by(auto_id=auto_id).all()
    order_entries = OrderEntry.query.filter_by(auto_id=auto_id).all()
    if len(orders) > 0 or len(order_entries) > 0:
        msg = "Невозможно удалить авто, так как с ним существуют заказы: "
        if len(orders) > 0:
            for order in orders:
                msg += "№" + str(order.order_id) + ", "
            return redirect(url_for('error_page', msg=msg))
        if len(order_entries) > 0:
            for order in order_entries:
                msg += "№" + str(order.order_id) + ", "
            return redirect(url_for('error_page', msg=msg))

    try:
        db.session.delete(auto)
        db.session.commit()
        return redirect('/autos-list')
    except:
        return "Error happened"


# Orders Pages


@app.route('/create-order', methods=['POST', 'GET'])
def order_create():
    if request.method == "POST":
        client_id = request.form['client_id']
        auto_id = request.form['auto_id']

        new_order = Order(client_id=client_id, auto_id=auto_id)

        try:
            db.session.add(new_order)
            db.session.commit()
            return redirect('/orders-list')
        except:
            return "Error happened"
    else:
        autos = Auto.query.order_by(Auto.auto_id).all()
        clients = Client.query.order_by(Client.client_id).all()
        return render_template("create-order.html", autos=autos, clients=clients)


@app.route('/orders-list')
def orders_list():
    orders = Order.query.order_by(Order.order_id).all()
    return render_template("orders-list.html", orders=orders)


@app.route('/orders-list/<int:order_id>/detail', methods=['POST', 'GET'])
def order_change_information(order_id):
    order = Order.query.get(order_id)
    client = Client.query.get_or_404(order.client_id)
    auto = Auto.query.get_or_404(order.auto_id)

    completed = False
    sales = Sale.query.filter_by(order_id=order_id).all()
    if len(sales) > 0:
        completed = True
    if request.method == "POST":
        adding = request.form['auto_id']
        entry = OrderEntry(order_id=order_id, auto_id=adding)
        try:
            db.session.add(entry)
            db.session.commit()
        except:
            return "Error happened"
        return redirect(url_for('order_change_information', order_id=order_id))
    else:
        entries = OrderEntry.query.filter_by(order_id=order_id)
        temp = []
        for entry in entries:
            obj = Auto.query.filter_by(auto_id=entry.auto_id)
            temp.append(obj)
        added_autos = temp
        autos = Auto.query.order_by(Auto.auto_id).all()
        return render_template("order-information.html",
                               order=order, client=client, auto=auto, autos=autos,
                               added_autos=added_autos, completed=completed)


@app.route('/orders-list/<int:order_id>/delete')
def order_delete(order_id):
    order = Order.query.get_or_404(order_id)

    sales = Sale.query.filter_by(order_id=order_id).all()
    if len(sales) > 0:
        return redirect(url_for('error_page', msg="Невозможно удалить заказ, так как он уже завершен"))

    entries = OrderEntry.query.filter_by(order_id=order_id).all()
    entries_amount = len(entries)
    for i in range(0, entries_amount):
        entry = OrderEntry.query.filter_by(order_id=order_id).first()
        try:
            db.session.delete(entry)
            db.session.commit()
        except:
            redirect(url_for('error_page', msg="Невозможно удалить OrderEntry"))

    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/orders-list')
    except:
        return "Error happened"


@app.route('/orders-list/<int:order_id>/delete/<int:auto_id>/delete-auto')
def order_delete_auto(order_id, auto_id):
    entries = OrderEntry.query.filter_by(order_id=order_id)
    for en in entries:
        if en.auto_id == auto_id:
            try:
                db.session.delete(en)
                db.session.commit()
                return redirect(url_for('order_change_information', order_id=order_id))
            except:
                return "Error happened"


@app.route('/complete-order/<int:order_id>')
def order_complete(order_id):
    order = Order.query.get(order_id)
    order_auto = Auto.query.get_or_404(order.auto_id)

    cost = order_auto.price
    entries = OrderEntry.query.filter_by(order_id=order_id).all()
    for entry in entries:
        obj = Auto.query.filter_by(auto_id=entry.auto_id).first()
        cost += obj.price

    sale = Sale(order_id=order_id, sale_cost=cost)

    try:
        db.session.add(sale)
        db.session.commit()
    except:
        message = "Не удалось добавить продажу по заказу №" + str(order_id)
        return redirect('error_page', msg=message)

    if len(entries) > 0:
        new_sale = Sale.query.filter_by(order_id=order_id).first()
        sale_id = new_sale.sale_id

        sale_entry = SaleEntry(sale_id=sale_id, auto_id=order_auto.auto_id)
        try:
            db.session.add(sale_entry)
            db.session.commit()
        except:
            message = "Не удалось добавить SaleEntry по продаже №" + str(sale_id)
            return redirect('error_page', msg=message)

        for entry in entries:
            auto_id = entry.auto_id
            sale_entry = SaleEntry(sale_id=sale_id, auto_id=auto_id)
            try:
                db.session.add(sale_entry)
                db.session.commit()
            except:
                message = "Не удалось добавить SaleEntry по продаже №" + str(sale_id)
                return redirect('error_page', msg=message)
        return redirect(url_for('order_change_information', order_id=order_id))


# Dev Pages


@app.route('/all-tables')
def all_tables():
    clients = Client.query.order_by(Client.client_id).all()
    autos = Auto.query.order_by(Auto.auto_id).all()
    orders = Order.query.order_by(Order.order_id).all()
    sales = Sale.query.order_by(Sale.sale_id).all()
    order_entries = OrderEntry.query.order_by(OrderEntry.order_entry_id).all()
    sale_entries = SaleEntry.query.order_by(SaleEntry.sale_entry_id).all()

    return render_template("all-tables.html",
                           clients=clients, autos=autos, orders=orders, sales=sales,
                           order_entries=order_entries, sale_entries=sale_entries)


@app.route('/error/<msg>')
def error_page(msg):
    return render_template("error-page.html", message=msg)


# Sales Pages


@app.route('/reports')
def show_reports():
    sales = Sale.query.order_by(Sale.sale_id).all()
    return render_template("reports.html", sales=sales)


@app.route('/show-pts/<int:sale_id>')
def show_pts(sale_id):
    sale = Sale.query.get(sale_id)
    sale_entries = SaleEntry.query.filter_by(sale_id=sale_id).all()
    order = Order.query.get_or_404(sale.order_id)
    client = Client.query.get_or_404(order.client_id)
    added_autos = []
    for entry in sale_entries:
        obj = Auto.query.filter_by(auto_id=entry.auto_id).first()
        added_autos.append(obj)
    return render_template("pts.html", sale=sale, client=client, added_autos=added_autos)


@app.route('/show-cost/<int:sale_id>')
def show_cost_report(sale_id):
    sale = Sale.query.get(sale_id)
    order = Order.query.get_or_404(sale.order_id)
    client = Client.query.get_or_404(order.client_id)
    sale_entries = SaleEntry.query.filter_by(sale_id=sale_id).all()
    added_autos = []
    for entry in sale_entries:
        obj = Auto.query.filter_by(auto_id=entry.auto_id).first()
        added_autos.append(obj)
    return render_template("cost.html", sale=sale, added_autos=added_autos, client=client)


if __name__ == '__main__':
    app.run()
