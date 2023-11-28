
#include "geant4/Application.h"

#include <iostream>

using namespace std;
using namespace geant4;

Application::Application() : runManager() {
    // runManager will manage the lifetime of the following objects
    runManager.SetUserInitialization(new DetectorConstruction());
    runManager.SetUserInitialization(new PhysicsList());

    runManager.SetUserAction(new PrimaryGeneratorAction());
    runManager.SetUserAction(new SteppingAction());
    runManager.SetUserAction(new TrackingAction());
    runManager.SetUserAction(new EventAction());
}

void Application::Initialize() {
    runManager.Initialize();
}

void Application::Run(unsigned int nEvents) {
    runManager.BeamOn(nEvents);
}
