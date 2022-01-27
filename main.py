from flask import Flask, get_flashed_messages, redirect, request, render_template, url_for, flash
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
import json
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

app.config["SECRET_KEY"] = "dhjbcjdshbcds skbjcksd"

try:
    mongo = pymongo.MongoClient(host="localhost", port=27017, serverSelectionTimeoutMS=1000)
    db = mongo.exploration
    mongo.server_info()
except:
    print("Error - Cannot connect to db")

class FuelConsumptionData(Resource):
    def get(self):
        datas = db.data.find()
        vehicleDict = {}
        for data in datas:
            for vehicle in data["vehicle"]:
                for eachDay in range(len(data["vehicle"][vehicle]["dateArray"])):
                    if data["vehicle"][vehicle]["dateArray"][eachDay] not in vehicleDict.keys():
                        vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]] = {vehicle: data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]}
                    else:
                        if vehicle in vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]].keys():
                            vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] += data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                        else:
                            vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] = data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
        graph1 = []
        for date in vehicleDict:
            totalPetrol = 0
            for vehicle in vehicleDict[date]:
                totalPetrol+=vehicleDict[date][vehicle]
            graph1.append([date, totalPetrol])
        print(graph1)
        print("Sent as request data: ", graph1)
        return {"data": graph1}

api.add_resource(FuelConsumptionData, "/api/fuelconsumptiondata")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        user = db.users.find_one({"username": username})
        print(user)
        if user:
            passwordHashed = user["password"]
            password = check_password_hash(passwordHashed, request.form.get('password'))
            print(username, password)
            if password:
                return redirect(url_for('users', username=username))
            else:
                flash("Invalid password!")
        else:
            flash("Username doesnot exist")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        fullName = request.form.get('fullName')
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'), method='sha256') 
        print(username, fullName, email, password)
        user = db.users.find_one({"username": username})
        email = db.users.find_one({"email": email})
        if not user and not email:
            newUser = {"username": username, "fullName": fullName, "email": email, "password": password}
            dbResponse = db.users.insert_one(newUser)
            print(dbResponse.inserted_id)
            return redirect(url_for('users', username=username))
        else:
            if user:
                print("User already exists")
                flash("User already exists")
            else:
                print("Email already exists")
                flash("User email already exists")
    return render_template("register.html")

@app.route('/', methods=["GET", "POST"])
def home():
    datas = db.data.find()
    users = db.users.find()
    vehicleDict = {}
    placeDict = {}
    vehicleAmount = {}
    for data in datas:
        for vehicle in data["vehicle"]:
            if vehicle not in vehicleAmount.keys():
                vehicleAmount[vehicle] = 1
            else:
                vehicleAmount[vehicle] += 1
            for eachDay in range(len(data["vehicle"][vehicle]["dateArray"])):
                if data["vehicle"][vehicle]["dateArray"][eachDay] not in vehicleDict.keys():
                    vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]] = {vehicle: data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]}
                else:
                    if vehicle in vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]].keys():
                        vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] += data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                    else:
                        vehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] = data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                if data["vehicle"][vehicle]["placeArray"][eachDay] not in placeDict.keys():
                    placeDict[data["vehicle"][vehicle]["placeArray"][eachDay]] = data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                else:
                    placeDict[data["vehicle"][vehicle]["placeArray"][eachDay]] += data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
    print(vehicleAmount)
    print(vehicleDict)
    print(placeDict)
    graph1 = []
    overallPetrol = 0
    for date in vehicleDict:
        totalPetrol = 0
        for vehicle in vehicleDict[date]:
            totalPetrol+=vehicleDict[date][vehicle]
            overallPetrol+=vehicleDict[date][vehicle]
        graph1.append([date, totalPetrol])
    print(graph1)
    # graph1.reverse()
    print(graph1)
    graph2 = []
    graph2Dict = {}
    for date in vehicleDict:
        for vehicle in vehicleDict[date]:
            if vehicle not in graph2Dict.keys():
                graph2Dict[vehicle] = vehicleDict[date][vehicle]
            else:
                graph2Dict[vehicle] += vehicleDict[date][vehicle]
    for vehicle in graph2Dict:
        graph2.append([vehicle, graph2Dict[vehicle]])
    print(graph2Dict)
    print(graph2)
    coEmissionToday = str(datetime.now())[0:10]
    coEmissionTodayVal = 0
    for dates in graph1:
        if dates[0]==coEmissionToday:
            coEmissionTodayVal = dates[1]
            break
    usercount = 0
    for i in users:
        usercount+=1
    return render_template("home.html", graph1=json.dumps(graph1) if graph1!=[] else None, graph2=json.dumps(graph2) if graph2!=[] else None, graph3=placeDict if placeDict!={} else None, graph4=vehicleAmount if vehicleAmount!={} else None, coEmissionToday=coEmissionTodayVal, averagePersonPollution=overallPetrol/usercount)

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/users/<string:username>', methods=["GET", "POST"])
def users(username):
    user = db.users.find_one({"username": username})
    if user:
        uid = ObjectId(user["_id"])
        data = db.data.find_one({"uid": uid})
        if data:
            uservehicleDict = {}
            costDict = {}
            for vehicle in data["vehicle"]:
                for eachDay in range(len(data["vehicle"][vehicle]["dateArray"])):
                    if data["vehicle"][vehicle]["dateArray"][eachDay] not in uservehicleDict.keys():
                        uservehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]] = {vehicle: data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]}
                        costDict[data["vehicle"][vehicle]["dateArray"][eachDay]] = {vehicle: data["vehicle"][vehicle]["costArray"][eachDay]}
                    else:
                        if vehicle in uservehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]].keys():
                            uservehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] += data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                            costDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] += data["vehicle"][vehicle]["costArray"][eachDay]
                        else:
                            uservehicleDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] = data["vehicle"][vehicle]["petrolConsumptionArray"][eachDay]
                            costDict[data["vehicle"][vehicle]["dateArray"][eachDay]][vehicle] = data["vehicle"][vehicle]["costArray"][eachDay]
            print(uservehicleDict)
            print(costDict)
            graph1 = []
            for date in uservehicleDict:
                totalPetrol = 0
                for vehicle in uservehicleDict[date]:
                    totalPetrol+=uservehicleDict[date][vehicle]
                graph1.append([date, totalPetrol])
            graph2 = []
            graph2Dict = {}
            for date in uservehicleDict:
                for vehicle in uservehicleDict[date]:
                    if vehicle not in graph2Dict.keys():
                        graph2Dict[vehicle] = uservehicleDict[date][vehicle]
                    else:
                        graph2Dict[vehicle] += uservehicleDict[date][vehicle]
            for vehicle in graph2Dict:
                graph2.append([vehicle, graph2Dict[vehicle]])
            print(graph2)
            graph3 = []
            for date in costDict:
                totalCost = 0
                for vehicle in costDict[date]:
                    totalCost+=costDict[date][vehicle]
                graph3.append([date, totalCost])
            graph4 = []
            graph4Dict = {}
            for date in costDict:
                for vehicle in costDict[date]:
                    if vehicle not in graph4Dict.keys():
                        graph4Dict[vehicle] = costDict[date][vehicle]
                    else:
                        graph4Dict[vehicle] += costDict[date][vehicle]
            for vehicle in graph4Dict:
                graph4.append([vehicle, graph4Dict[vehicle]])
            print(graph4)
            coEmission = 0
            for dates in graph1:
                if dates[0]==str(datetime.now())[0:10]:
                    coEmission = dates[1]
                    break
            return render_template("user.html", username=username, data=data if data else False, graph1=json.dumps(graph1) if graph1!=[] else None, graph2=json.dumps(graph2) if graph2!=[] else None, graph3=json.dumps(graph3) if graph3!=[] else None, graph4=json.dumps(graph4) if graph4!=[] else None, coEmission=coEmission)
        return render_template("user.html", username=username, data=False)
    return redirect(url_for('home'))

@app.route('/users/<string:username>/addNewVehicle', methods=["GET", "POST"])
def addNewVehicle(username):
    user = db.users.find_one({"username": username})
    # print(user)
    if user:
        uid = ObjectId(user["_id"])
        if request.method == "POST":
            print(request.form.get('vehicleName'), request.form.get('vehicleNumber'))
            vehicleName = request.form.get('vehicleName')
            vehicleNumber = request.form.get('vehicleNumber')
            vehicleName = list(vehicleName.split(','))
            vehicleNumber = list(vehicleNumber.split(','))
            vehicleDict = {}
            for vehicle in range(len(vehicleName)):
                print(vehicleName[vehicle])
                print(vehicleNumber[vehicle])
                vehicleDict[vehicleName[vehicle]] = {"petrolConsumptionArray":[], "dateArray":[], "costArray":[], "placeArray":[], "vehicle Number":vehicleNumber[vehicle]}
            print(vehicleDict)
            if not db.data.find_one({"uid": uid}):
                newData = {"uid": uid, "vehicle": vehicleDict}
                dbResponse = db.data.insert_one(newData)
                print(dbResponse.inserted_id)
            else:
                previousData = db.data.find_one({"uid": uid})
                vehicleDict.update(previousData["vehicle"])
                dbResponse = db.data.update_one({"uid": uid}, {"$set": {"vehicle": vehicleDict}})
            return redirect(url_for('users', username=username))
        return render_template("newVehicle.html", username=username)
    else:
        return redirect(url_for('home'))

@app.route('/users/<string:username>/addNewData', methods=["GET", "POST"])
def addNewData(username):
    user = db.users.find_one({"username": username})
    if user:
        uid = ObjectId(user["_id"])
        data = db.data.find_one({"uid": uid})
        if request.method == "POST":
            vehicleName = request.form.get('vehicleName')
            fuelConsumed = request.form.get('fuelConsumed')
            fuelCost = request.form.get('fuelCost')
            placeName = request.form.get('placeName')
            vehicleName = list(vehicleName.split(','))
            fuelConsumed = list(fuelConsumed.split(','))
            fuelCost = list(fuelCost.split(','))
            placeName = list(placeName.split(','))
            print(vehicleName, fuelConsumed, fuelCost, placeName)
            for index in range(len(vehicleName)):
                if str(datetime.now())[0:10] not in data["vehicle"][vehicleName[index]]["dateArray"]:
                    data["vehicle"][vehicleName[index]]["petrolConsumptionArray"].append(int(fuelConsumed[index]))
                    data["vehicle"][vehicleName[index]]["dateArray"].append(str(datetime.now())[0:10])
                    data["vehicle"][vehicleName[index]]["costArray"].append(int(fuelCost[index]))
                    data["vehicle"][vehicleName[index]]["placeArray"].append(placeName[index])
                else:
                    dataArrayIndex = data["vehicle"][vehicleName[index]]["dateArray"].index(str(datetime.now())[0:10])
                    data["vehicle"][vehicleName[index]]["petrolConsumptionArray"][dataArrayIndex]+=int(fuelConsumed[index])
                    data["vehicle"][vehicleName[index]]["costArray"][dataArrayIndex]+=(int(fuelCost[index]))
            dbResponse = db.data.update_one({"uid": uid}, {"$set": {"vehicle": data["vehicle"]}})
            print(dbResponse)
            return redirect(url_for('users', username=username))
        return render_template("newData.html", username=username, data=data)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)