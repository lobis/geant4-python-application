
#ifndef LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H
#define LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H

#include <G4VUserActionInitialization.hh>

class ActionInitialization : public G4VUserActionInitialization {
public:
    ActionInitialization();

    void BuildForMaster() const override;
    void Build() const override;
};


#endif//LIBGEANT4PYTHONICAPPLICATION_ACTIONINITIALIZATION_H
