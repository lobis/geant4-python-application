

#ifndef GEANT4_APPLICATION_H
#define GEANT4_APPLICATION_H

#include "RunManager.h"

#include "DetectorConstruction.h"
#include "EventAction.h"
#include "PhysicsList.h"
#include "PrimaryGeneratorAction.h"
#include "SteppingAction.h"
#include "TrackingAction.h"

namespace geant4 {

    class Application {
    private:
        RunManager runManager;

    public:
        Application();
        ~Application() = default;

        void Initialize();
        void Run(unsigned int nEvents);
    };

}// namespace geant4

#endif//GEANT4_APPLICATION_H
