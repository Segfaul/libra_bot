import json
import os

import pandas as pd
from flask import Flask, request, send_from_directory

from database.dbapi import DatabaseConnector
from database.models import Borrow

app = Flask(__name__)

USERNAME = "agentric"


@app.route("/download/<book_id>")
def download_book_statistics(book_id):
    try:        
        filename = f"borrow_stats_of_book_id_{book_id}.xlsx"
        return send_from_directory(os.getcwd() , filename, as_attachment=True)

    except Exception as e:
        print(repr(e))
        return json.dumps({"message": str(e)}, ensure_ascii=False), 500


@app.route("/borrow/stats", methods=['POST'])
def ceate_book_statistics():
    if request.method == 'POST':
        try:
            db = DatabaseConnector()
            session = db.Session()

            book_id = request.json['book_id']
            book_id = int(book_id)
            borrows = session.query(Borrow.borrow_id, Borrow.book_id, Borrow.date_start, Borrow.date_end).filter(Borrow.book_id == book_id).all() 

            if borrows == None or len(borrows) == 0:
                return json.dumps({"message": "not found"}, ensure_ascii=False), 404

            filename = f"borrow_stats_of_book_id_{book_id}.xlsx"
            filename = os.path.join(os.getcwd(), filename)
            pd.DataFrame([borrow._asdict() for borrow in borrows]).to_excel(filename)

            return json.dumps({"message": "otsosite"}, ensure_ascii=False), 200
        except Exception as e:
            print(repr(e))
            return json.dumps({"message": str(e)}, ensure_ascii=False), 500


# if __name__ == '__main__':
#     app.run("0.0.0.0", port=8080)
