<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Default Polygon</Name>
    <UserStyle>
      <Name>Default Polygon</Name>
      <Title>Default Polygon</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>&gt;= 0 and &lt; 1</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>0</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>1</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#f7fbff</CssParameter>
              <CssParameter name="fill-opacity">0</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 1 and &lt; 2</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>1</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>2</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#00ffff</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 2 and &lt; 5</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>2</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>5</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#00c2ff</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 5 and &lt; 7</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>5</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>7</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#1931b1</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 7 and &lt; 10</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>7</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>10</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#81ffb0</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 10 and &lt; 15</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>10</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>15</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#0ac15d</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 15 and &lt; 20</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>15</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>20</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#44824b</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 20 and &lt; 25</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>20</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>25</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#055b02</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 25 and &lt; 30</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>25</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>30</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#ffdd00</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 30 and &lt; 40</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>30</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>40</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#ffb200</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 40 and &lt; 50</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>40</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>50</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#ff9700</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 50 and &lt; 75</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>50</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>75</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#bf7202</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 75 and &lt; 100</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>75</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>100</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e5bfe8</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 100 and &lt; 150</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>100</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>rain</PropertyName>
                <Literal>150</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e63890</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 150 and &lt;= 250</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>150</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>rain</PropertyName>
                <Literal>250</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#9b00ff</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">0.1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>