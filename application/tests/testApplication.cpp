
#include "geant4/Application.h"
#include <gtest/gtest.h>
#include <iostream>

using namespace std;
using namespace geant4;

const std::string gdml = R"(
<?xml version="1.0" encoding="utf-8" standalone="no" ?>

<gdml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd">

    <define>
        <constant name="worldSize" value="1000"/>
        <constant name="boxSize" value="500"/>
    </define>

    <solids>
        <box name="WorldSolid" x="worldSize" y="worldSize" z="worldSize" lunit="mm"/>
        <box name="boxSolid" x="boxSize" y="boxSize" z="boxSize" lunit="mm"/>
    </solids>

    <structure>
        <volume name="boxVolume">
            <materialref ref="G4_WATER"/>
            <solidref ref="boxSolid"/>
        </volume>

        <volume name="World">
            <materialref ref="G4_AIR"/>
            <solidref ref="WorldSolid"/>

            <physvol name="box">
                <volumeref ref="boxVolume"/>
                <position name="boxPosition" unit="mm" x="0" y="0" z="0"/>
            </physvol>

        </volume>
    </structure>

    <setup name="Default" version="1.0">
        <world ref="World"/>
    </setup>
</gdml>
)";

TEST(Application, Run) {
    Application app;
    EXPECT_FALSE(app.IsSetup());
    app.SetupManager();
    EXPECT_FALSE(app.IsSetup());
    app.SetupDetector<string, set<string>>(gdml, {"boxVolume"});
    EXPECT_FALSE(app.IsSetup());
    app.SetupPhysics();
    EXPECT_FALSE(app.IsSetup());
    app.SetupAction();
    EXPECT_TRUE(app.IsSetup());

    EXPECT_FALSE(app.IsInitialized());
    app.Initialize();
    EXPECT_TRUE(app.IsInitialized());

    app.Run(100);
}
