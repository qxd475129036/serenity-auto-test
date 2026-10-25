package com.example.autotest.features.cucumber;

import io.cucumber.junit.platform.engine.Constants;
import org.junit.jupiter.api.Tag;
import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectPackages;
import org.junit.platform.suite.api.Suite;

@Suite
@IncludeEngines("cucumber")
@SelectPackages("features")
@ConfigurationParameter(
        key = Constants.PLUGIN_PROPERTY_NAME,
        value = "net.serenitybdd.cucumber.core.plugin.SerenityReporterParallel"
)
@ConfigurationParameter(
        key = Constants.GLUE_PROPERTY_NAME,
        value = "com.example.autotest.features.cucumber"
)
@ConfigurationParameter(
        key = Constants.PARALLEL_EXECUTION_ENABLED_PROPERTY_NAME,
        value = "true"
)
@ConfigurationParameter(
        key = Constants.PARALLEL_CONFIG_STRATEGY_PROPERTY_NAME,
        value = "dynamic"
)
@Tag("demo")
@Tag("cucumber")
class CucumberOrderApiTest {
}
