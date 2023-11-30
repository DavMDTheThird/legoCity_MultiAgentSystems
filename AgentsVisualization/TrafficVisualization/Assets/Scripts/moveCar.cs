/*
    Autor: David Medina Domínguez
        Matrícula: A01783155
    Autor: Natalia Maya Bolaños
        Matrícula: A01781992
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class moveCar : MonoBehaviour{
    GameObject[] wheels = new GameObject[4];


    [SerializeField] GameObject wheel_prefav;

    [SerializeField] float angle;
    [SerializeField] AXIS rotationAxis;


    Mesh[] mesh = new Mesh[4];
    Mesh car_mesh;
    Vector3[][] baseVertices = new Vector3[4][];
    Vector3[] car_baseVertices;
    Vector3[][] newVertices = new Vector3[4][];
    Vector3[] car_newVertices;

    Vector3[] wheelsPos = new Vector3[4];

    // Start is called before the first frame update
    public void Init(){
        wheelsPos[0] = new Vector3(-0.22f, 0.05f, 0.32f);
        wheelsPos[1] = new Vector3(0.22f, 0.05f, 0.32f);
        wheelsPos[2] = new Vector3(-0.22f, 0.05f, -0.27f);
        wheelsPos[3] = new Vector3(0.22f, 0.05f, -0.27f);

        for(int i = 0; i < wheels.Length; i++){
            wheels[i] = Instantiate(wheel_prefav, new Vector3(0f, 0f, 0f), Quaternion.identity);

            // Asigna el padre de las llantas   
            wheels[i].transform.parent = transform;

            // Crea el array de wheels, mesh y baseVertices
            mesh[i] = wheels[i].GetComponentInChildren<MeshFilter>().mesh;
            baseVertices[i] = mesh[i].vertices;

            // Crea el array de newVertices que contiene a todas las llantas
            newVertices[i] = new Vector3 [baseVertices[i].Length];
            for (int k = 0; k <baseVertices[i].Length; ++k){
                newVertices[i][k] = baseVertices[i][k];
            }   
        }
        car_mesh = GetComponentInChildren<MeshFilter>().mesh;
        car_baseVertices = car_mesh.vertices;

        // Create a copy of the original vertices
        car_newVertices = new Vector3 [car_baseVertices.Length];
        for (int i = 0; i <car_baseVertices.Length; ++i){
            car_newVertices[i] = car_baseVertices[i];
        }
    }

    // Update is called once per frame
    public void ApplyTransforms(Vector3 interpolated, Vector3 direction){
        //Debug.Log("ApplyTransforms");
        Matrix4x4 composite = DoTransform_Car(interpolated, direction, car_baseVertices, car_newVertices, car_mesh);
        for(int i = 0; i < wheels.Length; i++){
            DoTransform_Wheels(wheelsPos[i], rotationAxis, baseVertices[i], newVertices[i], mesh[i], composite);
        }
    }

    void DoTransform_Wheels(Vector3 wheelsPos, AXIS rotationAxis, Vector3[] baseVertices, Vector3[] newVertices, Mesh mesh, Matrix4x4 car_composite){
        Matrix4x4 rotate = HW_Transforms.RotateMat(angle * Time.time, rotationAxis);

        Matrix4x4 posObject = HW_Transforms.TranslationMat(wheelsPos.x,
                                                           wheelsPos.y,
                                                           wheelsPos.z);

        Matrix4x4 composite = car_composite * posObject * rotate;

        for (int i = 0; i < newVertices.Length; i++){
            Vector4 temp = new Vector4(baseVertices[i].x,
                                       baseVertices[i].y, 
                                       baseVertices[i].z,
                                       1);

            newVertices[i] = composite * temp;
        }
        // Replace the vertices in the mesh
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
    }

    Matrix4x4 DoTransform_Car(Vector3 car_displacement, Vector3 direction, Vector3[] car_baseVertices, Vector3[] car_newVertices, Mesh car_mesh){
        float ang = Mathf.Atan2(-direction.x, direction.z) * Mathf.Rad2Deg;


        Matrix4x4 move = HW_Transforms.TranslationMat(car_displacement.x,
                                                      car_displacement.y,
                                                      car_displacement.z);

        Matrix4x4 rotate = HW_Transforms.RotateMat(ang, AXIS.Y);

        Matrix4x4 composite = move * rotate;

        for (int i = 0; i < car_newVertices.Length; i++){
            Vector4 temp = new Vector4(car_baseVertices[i].x,
                                       car_baseVertices[i].y, 
                                       car_baseVertices[i].z,
                                       1);

            car_newVertices[i] = composite * temp;
        }
        // Replace the vetices in the car_mesh
        car_mesh.vertices = car_newVertices;
        car_mesh.RecalculateNormals();

        return composite;
    }
}
