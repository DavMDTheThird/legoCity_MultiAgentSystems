using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CityMaker : MonoBehaviour
{
    // [SerializeField] GameObject[] carPrefab;
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject[] buildingPrefab;
    [SerializeField] GameObject semaphorePrefab;
    [SerializeField] int tileSize;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    // Update is called once per frame
    void Update()
    {

    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length - 2;
        Debug.Log(y);

        Vector3 position;
        GameObject tile;

        for (int i = 0; i < tiles.Length; i++)
        {
            if (tiles[i] == '>' || tiles[i] == '<' || tiles[i] == 'C')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'v' || tiles[i] == '^' || tiles[i] == 'g' || tiles[i] == 'h' || tiles[i] == 'n' || tiles[i] == 'b')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'r' || tiles[i] == 'u' || tiles[i] == 'l' || tiles[i] == 'd')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);//Esto cambia
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.Euler(270, 0, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'R' || tiles[i] == 'U' || tiles[i] == 'L' || tiles[i] == 'D')
            {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0)); //Esto cambia
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.Euler(270, 0, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'T')
            {
                int rand = Random.Range(0, buildingPrefab.Length);

                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.Euler(0, 90, 0));
                tile.GetComponentInChildren<Renderer>().materials[0].color = Color.red;
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '#')
            {
                int rand = Random.Range(0, buildingPrefab.Length);

                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.identity);
                tile.transform.localScale = new Vector3(1, Random.Range(0.5f, 2.0f), 1);
                tile.transform.parent = transform;
                x += 1;
            }

            else if (tiles[i] == '\n')
            {
                x = 0;
                y -= 1;
            }
        }

    }
}
