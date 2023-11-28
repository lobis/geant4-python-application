
#include "geant4/Application.h"
#include <gtest/gtest.h>
#include <iostream>

using namespace std;
using namespace geant4;

TEST(Application, Run) {
    Application app;
    app.Initialize();
    app.Run(100);
}
