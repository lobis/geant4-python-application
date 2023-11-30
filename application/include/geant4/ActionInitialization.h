
#ifndef LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H
#define LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H

#include <G4VSteppingVerbose.hh>
#include <G4VUserActionInitialization.hh>

class ActionInitialization : public G4VUserActionInitialization {
public:
    ActionInitialization();

    void BuildForMaster() const override;
    void Build() const override;

    G4VSteppingVerbose* InitializeSteppingVerbose() const override;
};


#endif//LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H
