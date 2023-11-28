from flask import Flask, request, jsonify
from randomAgents.model import CityModel
from randomAgents.agent import Car, Traffic_Light, Destination, Obstacle, Road, Car_Generator

app = Flask("Traffic example")

@app.route('/init', methods=['POST'])
def initModel():
    global randomModel, currentStep

    currentStep = 0

    if request.method == 'POST':
        randomModel = CityModel()

        return jsonify({"message":"Model initialized."})

@app.route('/getCars', methods=['GET'])
def getCars():
    global randomModel

    if request.method == 'GET':
        # carPositions = [{"id": str(s.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in randomModel.grid.coord_iter() for s in a if isinstance(s, Car)]
        carPositions = [{"id": str(a.unique_id), "x": a.pos[0], "y":1, "z":a.pos[1]} for a in randomModel.schedule.agents if isinstance(a, Car)]

        return jsonify({'positions':carPositions})

@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global randomModel

    if request.method == 'GET':
        trafficLights = [{"id": str(a.unique_id), "x": a.pos[0], "y":1, "z":a.pos[1], "state": a.state, "direction": a.direction} for a in randomModel.schedule.agents if isinstance(a, Traffic_Light)]

        return jsonify({'positions':trafficLights})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)