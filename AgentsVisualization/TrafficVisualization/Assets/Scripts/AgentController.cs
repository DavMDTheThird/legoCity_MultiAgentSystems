// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id, direction;
    public float x, y, z;
    public bool state;

    public AgentData(string id){
        this.id = id;
    }

    public AgentData(string id, float x, float y, float z){
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public AgentData(string id, float x, float y, float z, bool state, string direction){
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;
        this.direction = direction;
    }
}

[Serializable]
public class AgentsData{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    string getAgentsEndpoint = "/getCars";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string getRoadsEndpoint = "/getRoads";
    string getDestinationsEndpoint = "/getDestinations";
    string getArrivedCars = "/getArrivedCars";
    string getObstaclesEndpoint = "/getObstacles";
    AgentsData agentsData, obstacleData, roadsData, destinationData, ArrivedCars, trafficLightsData;
    Dictionary<string, GameObject> agentsDIC, trafficLightsDIC;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    [SerializeField] GameObject[] obstaclePrefab;
    public GameObject agentPrefab, floor, trafficLightPrefab;
    List<GameObject> deleteCars;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start(){
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        destinationData = new AgentsData();
        roadsData = new AgentsData();

        deleteCars = new List<GameObject>();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agentsDIC = new Dictionary<string, GameObject>();
        trafficLightsDIC = new Dictionary<string, GameObject>();
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update(){
        if(timer < 0){
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated){
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions.
            // The positions are interpolated between the previous and current positions.
            foreach(var agent in currPositions){
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agentsDIC[agent.Key].GetComponent<moveCar>().ApplyTransforms(interpolated, direction);
                // agents[agent.Key].transform.localPosition = interpolated;
                // if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

    IEnumerator UpdateSimulation(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetDestroyCars());
            StartCoroutine(ChangeTrafficLights());
            DestroyCars();
        }
    }

    IEnumerator SendConfiguration(){
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success){
            Debug.Log(www.error);
        }
        else{
            // Debug.Log("Configuration upload complete!");
            // Debug.Log("Getting Agents positions");

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetTrafficLights());
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetDestinationsData());
            StartCoroutine(GetRoadData());
        }
    }

    IEnumerator GetAgentsData(){
        // The GetAgentsData method is used to get the agents data from the server.

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions){
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                    
                Vector3 currentPosition = new Vector3();
                // Esto es que encuentre si existe en el diccionario
                if(currPositions.TryGetValue(agent.id, out currentPosition))
                    prevPositions[agent.id] = currentPosition;
                else{ // Pos si no existe, que lo cree y que lo agregue al diccionario
                    prevPositions[agent.id] = newAgentPosition;
                    agentsDIC[agent.id] = Instantiate(agentPrefab, Vector3.zero, Quaternion.identity);
                    agentsDIC[agent.id].GetComponent<moveCar>().Init();
                    agentsDIC[agent.id].GetComponent<moveCar>().ApplyTransforms(newAgentPosition, Vector3.zero);
                }
                currPositions[agent.id] = newAgentPosition;
            }

            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetObstacleData(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(obstacleData.positions);

            foreach(AgentData obstacle in obstacleData.positions){
                int rand = UnityEngine.Random.Range(0, obstaclePrefab.Length);
                Instantiate(obstaclePrefab[rand], new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
                Instantiate(floor, new Vector3(obstacle.x, obstacle.y - 0.04f, obstacle.z), Quaternion.identity);
            }
        }
    }

    void DestroyCars(){
        foreach(GameObject car in deleteCars){
            Destroy(car);
            deleteCars.Remove(car);
        }
    }

    IEnumerator GetDestroyCars(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getArrivedCars);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            ArrivedCars = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log("Arrived car: " + ArrivedCars.positions);

            foreach(AgentData arrivedCar in ArrivedCars.positions){
                deleteCars.Add(agentsDIC[arrivedCar.id]);
                agentsDIC.Remove(arrivedCar.id);
                currPositions.Remove(arrivedCar.id);
                prevPositions.Remove(arrivedCar.id);
            }
        }
    }

    IEnumerator GetDestinationsData(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDestinationsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            destinationData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(destinationData.positions);

            foreach(AgentData obstacle in destinationData.positions){
                int rand = UnityEngine.Random.Range(0, obstaclePrefab.Length);
                GameObject tile = Instantiate(obstaclePrefab[rand], new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
                tile.GetComponentInChildren<Renderer>().materials[0].color = Color.red;
                Instantiate(floor, new Vector3(obstacle.x, obstacle.y - 0.04f, obstacle.z), Quaternion.identity);
                // tile.transform.parent = transform; // Este no se si lo necesite (creo que no)
            }
        }
    }

    IEnumerator GetRoadData(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRoadsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            roadsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(roadsData.positions);

            foreach(AgentData obstacle in roadsData.positions){
                Instantiate(floor, new Vector3(obstacle.x, obstacle.y - 0.04f, obstacle.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetTrafficLights(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            trafficLightsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData tf in trafficLightsData.positions){
                trafficLightsDIC[tf.id] = Instantiate(trafficLightPrefab, new Vector3(tf.x, tf.y, tf.z), Quaternion.Euler(-90, 0, 0));
                trafficLightsDIC[tf.id].GetComponentInChildren<Light>().color = Color.red;

            }
        }
    }

    IEnumerator ChangeTrafficLights(){
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else{
            trafficLightsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData tf in trafficLightsData.positions){
                if(tf.state){
                    trafficLightsDIC[tf.id].GetComponentInChildren<Light>().color = new Color32(61, 161, 27, 255);
                }
                else{
                    trafficLightsDIC[tf.id].GetComponentInChildren<Light>().color = Color.red;
                }
            }
        }
    }
}