import sqlite3

def log(file, str):
    file.write(str + "\n")
    print(str)

def read_file(infile, outfile, sender):

    #ログファイル準備
    logFile = open("../../log/02出品登録.log","w")
    log(logFile, "ログファイルopen")

    #入力ファイル
    csvFile = open(infile,"r")
    log(logFile, "入力ファイルopen：" + infile)

    #ＤＢを開く
    connection = sqlite3.connect("../../db/resale.db")
    cursor = connection.cursor()
    log(logFile, "ＤＢopen")

    try:

        #１行目はヘッダ
        line = csvFile.readline()
        listHeader = line
        csvResult = ""

        #１行ずつ処理
        line = csvFile.readline()
        while line:

            #結果データに追加
            csvResult = csvResult + line

            #ＣＳＶデータを展開
            data = line.split(",")
            if len(data) < 4:
                continue
            yahoo_item_id = data[0]
            amazon_item_asin = data[1]
            amazon_price_max = data[2]
            amazon_stock_min = data[3]

            #データの重複チェック
            itemValue = (yahoo_item_id,)
            cursor.execute("select yahoo_item_id from item_resale where yahoo_item_id=?",itemValue)
            if len(cursor.fetchall()) > 0:
                #既にある場合は、エラーを結果に出力して、次のデータへ
                csvResult = csvResult + ",既に登録済み"
                line = csvFile.readline()
                continue

            #ヤフオクの商品ＵＲＬ取得
            yahoo_item_url = "https://page.auctions.yahoo.co.jp/jp/auction/" + yahoo_item_id

            #Amazonの商品ＵＲＬ取得
            amazon_item_url = "https://www.amazon.co.jp/dp/" + amazon_item_asin

            #ＤＢへ書き込み
            values = []
            values.append(yahoo_item_id)
            values.append(yahoo_item_url)
            values.append(amazon_item_asin)
            values.append(amazon_item_url)
            values.append(amazon_price_max)
            values.append(amazon_stock_min)
            values.append(sender)
            sqlb = []
            sqlb.append("insert into item_resale (")
            sqlb.append("  yahoo_item_id")
            sqlb.append(" ,yahoo_item_url")
            sqlb.append(" ,amazon_item_asin")
            sqlb.append(" ,amazon_item_url")
            sqlb.append(" ,amazon_price_max")
            sqlb.append(" ,amazon_stock_min")
            sqlb.append(" ,sender")
            sqlb.append(" ,update_date")
            sqlb.append(") values (")
            sqlb.append(" datetime('now', 'localtime') ")
            sqlb.append(" ,?,?,?,?,?,?,? ")
            sqlb.append(") ")
            sql = "".join(sqlb)
            cursor.execute(sql, values)
            connection.commit()

            #結果を追記
            csvResult = csvResult + ",登録完了"

            #次の１行を読みこみ
            line = csvFile.readline()

        #結果をファイルに出力
        resultFile = open(outfile, "w")
        resultFile.write(listHeader + csvResult)
        resultFile.close()

    except:
        log(logFile, "エラー")

    finally:
        connection.close()
        log(logFile, "ＤＢクローズＯＫ")
        csvFile.close()
        log(logFile, "ＣＳＶファイルクローズＯＫ")
        logFile.close()

