using UnityEngine;

public class cameraMovement : MonoBehaviour
{
    //sensitivity is how fast the camera moves depending on mouse input
    public float sensitivity;

    //maxVerticalAngle controls the range that the camera can look in up and down
    public float maxVerticalAngle;

    Camera cam;
    GameObject player;

    void Update()
    {
        move();
        cursorHandling();
    }


    void Start()
    {
        cam = GetComponent<Camera>();
        player = cam.transform.parent.gameObject;
    }


    //moves the camera every frame
    void move()
    {
        Vector3 playerEulerRotation = player.transform.rotation.eulerAngles;
        Vector3 playerChange = playerEulerRotation + (Vector3.down * -Input.GetAxis("Mouse X") * sensitivity);

        player.transform.rotation = Quaternion.Euler(playerChange);


        Vector3 camEulerRotation = cam.transform.rotation.eulerAngles;
        Vector3 camChange = camEulerRotation + (Vector3.left * Input.GetAxis("Mouse Y") * sensitivity);

        camChange = clamp(camChange);

        cam.transform.rotation = Quaternion.Euler(camChange);
    }


    //used to clamp the vertical angle to maxVerticalAngle
    Vector3 clamp(Vector3 newRotation)
    {
        float Xrotation = Mathf.Repeat(newRotation.x, 360) - 180; // (180 / -180 = forward), (-90 = down), (90 = up)

        //the value that the angle is clamped to, as the angle up and down is not the same as the angle unity uses
        float clampValue = 180 - maxVerticalAngle; 

        if (Xrotation < clampValue && Xrotation > 90) newRotation.x = clampValue + 180;
        if (Xrotation > -clampValue && Xrotation < -90) newRotation.x = -clampValue + 180;

        return newRotation;
    }

    //keeps the cursor hidden and locked to the screen
    void cursorHandling()
    {
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }
}
