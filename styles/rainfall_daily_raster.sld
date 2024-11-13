<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Opaque Raster</Name>
    <UserStyle>
      <Name>Opaque Raster</Name>
      <Title>Opaque Raster</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>Chuva Diária (mm/24h)</Name>
          <RasterSymbolizer>
            <Opacity>1</Opacity>
            <ColorMap type="intervals">
              <!--
              "#ffffff00", "#d5ffff", "#00d5ff", "#0080aa", "#0000b3",
              "#80ff55", "#00cc7f", "#558000", "#005500", "#ffff00",
              "#ffcc00", "#ff9900", "#d55500", "#ffbbff", "#ff2b80", "#8000aa"
              -->
              <ColorMapEntry color="#ffffff" quantity="0.99" label="0" opacity="0"/>
              <ColorMapEntry color="#00ffff" quantity="1" label="1" opacity="1"/>
              <ColorMapEntry color="#00c2ff" quantity="2" label="2" opacity="1"/>
              <ColorMapEntry color="#1931b1" quantity="5" label="5" opacity="1"/>
              <ColorMapEntry color="#81ffb0" quantity="7" label="7" opacity="1"/>
              <ColorMapEntry color="#0ac15d" quantity="10" label="10" opacity="1"/>
              <ColorMapEntry color="#44824b" quantity="15" label="15" opacity="1"/>
              <ColorMapEntry color="#055b02" quantity="20" label="20" opacity="1"/>
              <ColorMapEntry color="#ffdd00" quantity="25" label="25" opacity="1"/>
              <ColorMapEntry color="#ffb200" quantity="30" label="30" opacity="1"/>
              <ColorMapEntry color="#ff9700" quantity="40" label="40" opacity="1"/>
              <ColorMapEntry color="#bf7202" quantity="50" label="50" opacity="1"/>
              <ColorMapEntry color="#e5bfe8" quantity="75" label="75" opacity="1"/>
              <ColorMapEntry color="#e63890" quantity="100" label="100" opacity="1"/>
              <ColorMapEntry color="#9b00ff" quantity="250" label="250" opacity="1"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>