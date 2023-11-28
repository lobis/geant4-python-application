

#ifndef GEANT4_APPLICATION_H
#define GEANT4_APPLICATION_H

#include "G4RunManager.hh"

namespace geant4 {

    class Application {
    private:
        std::unique_ptr<G4RunManager> runManager = nullptr;
        bool isInitialized = false;

    public:
        Application();
        ~Application() = default;

        void Setup(const std::string& gdml);
        void Initialize();
        void Run(int nEvents);

        bool IsSetup() const;
        bool IsInitialized() const;
    };

}// namespace geant4

#endif//GEANT4_APPLICATION_H
