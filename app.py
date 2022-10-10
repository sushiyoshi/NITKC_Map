from curses import start_color
from tracemalloc import start
from flask import Flask, render_template
from mygraph import GraphApp
from map_linetrace import get_plot,Point
import sys
from coordinatesList import CoordinatesList
app = Flask(__name__)
@app.route("/")
def index():
    #現在地と目的地を入力
    result = get_node_path("正門","第一駐車場")
    #距離を取得
    weight = result[0]['weight']
    #経由するノードを取得
    path = result[0]['path'][::2]
    #経路を形成する点の座標リストを格納
    pathList = []
    relationships = list(result[1])
    coordinatesList = CoordinatesList(sys.argv[2])

    # 以下クソコ
    for current in relationships:
        #current = relationships[i]
        re = []
        table_name=current._properties['name']
        #座標リストデータベース上に該当する座標リストが存在したら
        if coordinatesList.isExistCoordinatesList(table_name):
            print("Get a coordinates list")
            re = coordinatesList.getCoordinatesList(table_name)
        else:
        #存在しなかったら、新たに座標リストを作成
            print("Create a new coordinates list")
            pointList =[]
            for node in current.nodes:
                index = "index_{}".format(node.id)
                j = current._properties[index] if index in current._properties else 0
                pointList.append(Point(node._properties['y'][j],node._properties['x'][j]))
            re = get_plot(pointList[0],pointList[1])
            coordinatesList.createCoordinatesList(table_name,re)
        pathList.extend(re)
    coordinatesList.close()
    return render_template("index.html",path=pathList)

def get_node_path(Area1,Area2):
    uri = "neo4j+s://cfa2fb67.databases.neo4j.io:7687"
    user = "neo4j"
    password = sys.argv[1]
    graphapp = GraphApp(uri, user, password)

    result = graphapp.find_shortestPath(Area1,Area2)
    graphapp.close()
    return result

if __name__ == "__main__":
    app.run(debug=True)