using System;
using UnityEngine;

public class ballThrow : MonoBehaviour
{
    GameObject camera;
    GameObject player;

    GameObject currentBall;
    float throwingForce = 1;

    public float ballDistance;

    public void Start()
    {
        camera = gameObject.transform.GetChild(0).gameObject;
        player = gameObject;

    }

    void Update()
    {
        if (Input.GetMouseButton(0)) throwingForce += Time.deltaTime * 2;
        if (Input.GetMouseButtonUp(0)) spawnBall();
    }

    void spawnBall()
    {
        Vector3 dirVec = getDirectionVector();

        if (currentBall != null) Destroy(currentBall);

        currentBall = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        currentBall.transform.position = dirVec + camera.transform.position;
        currentBall.AddComponent<ball>();

        currentBall.AddComponent<Rigidbody>();
        currentBall.AddComponent<SphereCollider>();
        currentBall.GetComponent<Rigidbody>().constraints = RigidbodyConstraints.FreezePosition | RigidbodyConstraints.FreezeRotation;

        currentBall.GetComponent<ball>().velocity = dirVec * (throwingForce + 1);
        throwingForce = 1;
    }

    Vector3 getDirectionVector()
    {
        float xRotation = camera.transform.rotation.eulerAngles.x;
        float yRotation = player.transform.rotation.eulerAngles.y;


        Vector3 direction = new Vector3 (xRotation, yRotation);

        Vector3 dirVec = Quaternion.Euler(direction) * Vector3.forward;

        return dirVec;
    }
}
