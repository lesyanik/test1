from app import db, Client, Auto


def fill_tables():
    auto1 = Auto(name="Золотое кольцо России", price=50000, code="10", manufacturer="145")
    auto2 = Auto(name="Тур де Франс", price=140000, code="14", manufacturer="556")
    try:
        db.session.add(auto1)
        db.session.add(auto2)
        db.session.commit()
    except:
        return

    client1 = Client(name="Иванов Иван Иванович", phone="88999999999", code="0315367456")
    client2 = Client(name="Александрова Александра Александровна", phone="88888888888", code="1232345654")
    try:
        db.session.add(client1)
        db.session.add(client2)
        db.session.commit()
    except:
        return


db.create_all()
fill_tables()
exit()
