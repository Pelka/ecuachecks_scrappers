def main():
    from data_desing import models, schemas

    record = schemas.ScraperRecordHandler.create(
        schema_type="ant",
        data={
            "id_number": "1234567890",
            "full_name": "John Doe",
            "license_type": "A",
            "expedition_date": "2021-01-01",
            "expiration_date": "2021-12-31",
            "points": "10.0",
            "total": "10.0",
        },
    )

    print(record.get_schema_type())


# def main():
#     new_query = ScraperQuery()

#     new_query.status = "pending"
#     new_query.creation_date = datetime.now()
#     new_query.expired_date = datetime.now() + timedelta(days=7)

#     new_result = ScraperResult()
#     new_result.type = "ant"
#     new_result.status = "running"

#     new_record = MinInterior()
#     new_record.full_name = "John Doe"
#     new_record.id_number = "1234567890"
#     new_record.doc_type = "Nacional"
#     new_record.background = False
#     new_record.certificate = "www.google.com"

#     new_record2 = Sri()
#     new_record2.id_number = "1234567890"
#     new_record2.full_name = "John Doe"
#     new_record2.message = "test message"
#     new_record2.firm_debts = 0.0
#     new_record2.disputed_debts = 0.0
#     new_record2.payment_facilities = 0.0

#     new_record3 = Senescyt()
#     new_record3.id_number = "1234567890"
#     new_record3.full_name = "John Doe"
#     new_record3.gender = True
#     new_record3.nationality = "ECUATORIANA"

#     sub_record = SenescytDegree()
#     sub_record.title = "Ingeniero en Sistemas"
#     sub_record.college = "Universidad de Cuenca"
#     sub_record.type = "PREGRADO"
#     sub_record.recognized_by = "Test Recognized By"
#     sub_record.register_num = "123"
#     sub_record.register_date = datetime.now()
#     sub_record.area = "Test Area"
#     sub_record.note = "Test Note"

#     new_query.results.append(new_result)
#     new_record.result = new_result
#     new_record2.result = new_result

#     new_record3.degrees.append(sub_record)
#     new_record3.result = new_result

#     with SessionLocal.begin() as session:
#         session.add_all(
#             [new_query, new_result, new_record, new_record2, new_record3, sub_record]
#         )
#         session.commit()


if __name__ == "__main__":
    main()
