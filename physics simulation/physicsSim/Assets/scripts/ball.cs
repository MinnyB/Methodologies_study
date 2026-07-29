using System.Collections.Generic;
using System.Linq;
using Unity.VisualScripting;
using UnityEngine;

public class ball : MonoBehaviour
{
    Vector3 acceleration = Vector3.zero;
    public Vector3 velocity = Vector3.zero;

    public Dictionary<string, Vector3> forces = new Dictionary<string, Vector3>();
    public Dictionary<GameObject, Vector3> touchingObjects = new Dictionary<GameObject, Vector3>();

    const float mass = 5;
    const float reboundForce = 0.6f;
    const float frictionCoefficient = 2f;


    private void Update()
    {
        applyGravity();
        applyReaction();
        applyFriction();
        accelerationUpdate();
        move();
    }

    void accelerationUpdate()
    {
        acceleration = getResultantForce() / mass;
        
        velocity = velocity + (acceleration * Time.deltaTime);

    }

    private void OnCollisionEnter(Collision collision)
    {


        if (collision.gameObject.name.ToLower() == "player") return;

        Vector3 normal = collision.contacts[0].normal;

        if (!touchingObjects.ContainsKey(collision.gameObject)) touchingObjects.Add(collision.gameObject, normal);

        Vector3 resultant = getResultantForce();

        foreach (string force in forces.Keys)
        {
            if (!force.Contains("Reaction")) continue;

            resultant = resultant - forces[force];
        }

        Vector3 perpendicularVelocity = Vector3.Project(velocity, normal);
        velocity = velocity - perpendicularVelocity;
    }
    private void OnCollisionExit(Collision collision)
    {
        List<GameObject> toRemove = new List<GameObject> ();
        touchingObjects.Remove(collision.gameObject);
        forces.Remove(collision.gameObject.name + "Reaction");

    }

    Vector3 getResultantForce()
    {
        Vector3 resultant = Vector3.zero;
        foreach (Vector3 force in forces.Values)
            resultant += force;
        

        return resultant;
    }

    void applyReaction()
    {
        if (touchingObjects.Count == 0) return;
        Vector3 resultant = getResultantForce();

        foreach(string force in forces.Keys)
        {
            if(!force.Contains("Reaction")) continue;

            resultant = resultant - forces[force];
        }

        foreach(GameObject collision in touchingObjects.Keys)
        {
            Vector3 normal = touchingObjects[collision];

            Vector3 force = Vector3.Project(resultant, -normal);

            string name = collision.name + "Reaction";
            if(forces.ContainsKey(name)) forces.Remove(name);
            forces.Add(name, -force);

        }
    }

    void applyFriction()
    {
        if (touchingObjects.Count == 0) return;

        Vector3 resultant = getResultantForce();
        List<string> reactionForces = new List<string>();
        foreach (string force in forces.Keys)
        {
            if (force.Contains("Reaction")) reactionForces.Add(force);
            if (!force.Contains("Friction")) continue;

            resultant = resultant - forces[force];
        }

        foreach (string reactionName in reactionForces)
        {
            Vector3 reactionForce = forces[reactionName];

            Vector3 parallelForce = Vector3.ProjectOnPlane(velocity, reactionForce.normalized);

            name = reactionName.Substring(0, reactionName.Length - 8) + "Friction";
            Vector3 appliedFriction = -parallelForce * frictionCoefficient;
            print(appliedFriction);
            if (forces.ContainsKey(name)) forces.Remove(name);
            if (appliedFriction.magnitude < 0.05) appliedFriction = Vector3.zero;
            if (velocity.magnitude < 0.05)
            {
                velocity = Vector3.zero;
                acceleration = Vector3.zero;
            }


            forces.Add(name, appliedFriction);


        }
    }

    void applyGravity()
    {
        if (forces.ContainsKey("GravityY")) forces.Remove("GravityY");
        if (forces.ContainsKey("GravityX")) forces.Remove("GravityX");

        Vector3 baseGravity = new Vector3(0, -9.81f * mass, 0);

        if (touchingObjects.Count == 0)
        {
            forces.Add("GravityY", baseGravity);
            return;
        }

        Vector3 highestNormal = Vector3.down;

        foreach (GameObject collision in touchingObjects.Keys) {
            Vector3 normal = touchingObjects[collision];
            if (normal.y > highestNormal.y) highestNormal = normal;
        }
        
        if (highestNormal.Equals(Vector3.zero)) return;

        Vector3 parallel = Vector3.ProjectOnPlane(baseGravity, -highestNormal);
        Vector3 perp = baseGravity - parallel;

        forces.Add("GravityX", parallel);
        forces.Add("GravityY", perp);


    }

    void move()
    { 
        transform.Translate(velocity * Time.deltaTime);
    }
}
