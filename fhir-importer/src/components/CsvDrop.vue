<template>
  <v-container>
    <v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field label="Coding System" variant="solo" v-model="codingSystem"></v-text-field>
        </v-col>
      </v-row>
      <v-col cols="12">
        <v-card class="pa-4" outlined tile @drop.prevent="handleDrop" @dragover.prevent @dragenter.prevent>
          Drop CSV File Here
        </v-card>
      </v-col>
    </v-row>
    <v-row v-if="headers.length !== 0">
      <v-col cols="12">
        <v-data-table :headers="headers" :items="items"></v-data-table>
      </v-col>
    </v-row>
    <v-row v-if="headers.length !== 0">
      <v-col cols="12">
        <v-table>
          <thead>
            <tr>
              <td>CSV Row</td>
              <td>FHIR Resource</td>
              <td>Resource parameter</td>
              <td>Data type</td>
              <td>Unit</td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="header in headers" :key="header.key">
              <td>{{ header.key }}</td>
              <td><v-combobox label="Resource" v-model="mapping[header.key]['resource']" :items="resourceItems"
                  variant="outlined"></v-combobox></td>
              <td><v-combobox label="parameter" v-model="mapping[header.key]['parameter']" :items="patientItems"
                  variant="outlined"></v-combobox></td>
              <td><v-combobox label="datatype" v-model="mapping[header.key]['datatype']" :items="datatypeItems"
                  variant="outlined"></v-combobox></td>
              <td><v-text-field label="Unit" v-model="mapping[header.key]['unit']" variant="outlined">
                </v-text-field></td>
            </tr>
          </tbody>
        </v-table>
      </v-col>
    </v-row>
    <v-row v-if="headers.length !== 0">
      <v-col cols="12">
        <v-textarea label="FHIR Resources" variant="solo"></v-textarea>
      </v-col>
    </v-row>
    <v-row v-if="headers.length !== 0">
      <v-col cols="12">
        <v-btn @click="onChange" color="green-darken-4">Upload</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useCsvStore } from '@/store/csv.ts'
import FHIR from "fhirclient";

export default {

  data() {
    return {
      codingSystem: "",
      items: [],
      resourceItems: ['Ignore', 'Observation', 'Patient'],
      patientItems: ['identifier', 'gender', 'deceased'],
      datatypeItems: ['Integer', 'Boolean', 'String'],
      headers: [],
      mapping: {},
    };
  },
  methods: {
    handleDrop(e) {
      const file = e.dataTransfer.files[0];
      this.parseCsv(file);
    },
    async createFhirResource(fhirData, resourceName) {
      const client = FHIR.client("http://localhost:8080/fhir/");
      const createFhirResource = await client.create(fhirData);
    },
    parseCsv(file) {
      const reader = new FileReader();
      const store = useCsvStore();
      reader.onload = (e) => {
        const text = e.target.result;
        const lines = text.split('\r\n');
        this.headers = lines[0].split(',').map(header => ({ title: header, value: header, key: header }));
        this.mapping = this.headers.reduce((mapping, header, idx) => (mapping[header.key] = {}, mapping), {});
        this.items = lines.slice(1).map(line => {
          const data = line.split(',');
          return this.headers.reduce((obj, header, index) => {
            obj[header.value] = data[index];
            return obj;
          }, {});
        });
        store.setCsvData(this.headers, this.items);
      };
      reader.readAsText(file);
    },
    onMounted() {
      this.createFhirResource
    },
    async onChange(e) {
      for (var item in this.items) {
        var theItem = this.items[item];
        var identifierValue = null
        var identifierCode = null
        var genderValue = null
        var deceasedValue = null
        var valueString = null
        var valueQuantity = null
        var valueBoolean = null
        for (var itemKey in theItem) {
          const resource = this.mapping[itemKey]['resource'];
          const parameter = this.mapping[itemKey]['parameter'];
          const datatype = this.mapping[itemKey]['datatype'];
          const unit = this.mapping[itemKey]['unit'];
          if (resource == "Patient") {
            if (parameter == "identifier") {
              identifierValue = theItem[itemKey];
              identifierCode = itemKey;
            }
            if (parameter == "gender") {
              genderValue = theItem[itemKey];
            }
            if (parameter == "deceased") {
              deceasedValueNumber = theItem[itemKey];
              if (deceasedValue == 1) {
                deceasedValueNumber = true
              }
              else if (deceasedValue == 0) {
                deceasedValueNumber = false
              }
            }
            const patientData = {
              "resourceType": "Patient",
              "identifier": [{
                "use": "usual",
                "type": {
                  "coding": [{
                    "system": this.codingSystem,
                    "code": identifierCode
                  }]
                },
                "value": identifierValue
              }],
              "gender": genderValue,
              "deceasedBoolean": deceasedValue,
            };
            //console.log(patientData)
            //await this.createFhirResource(patientData)
            const client = FHIR.client("http://localhost:8080/fhir/");
            const createFhirResource = await client.create(patientData);
          }
          if (resource == "Observation") {
            if (datatype == "String") {
              valueString = theItem[itemKey];
            } else if (datatype == "Integer") {
              valueQuantity = {
                "value": theItem[itemKey],
                "unit": unit,
                "system": this.codingSystem,
                "code": itemKey,
              };
            } else if (datatype == "Boolean") {
              valueBoolean = {
                "valueBoolean": theItem[itemKey],
              };
            }
            const observationData = {
              "resourceType": "Observation",
              /*"subject": {
                "reference": "Patient/" + identifierValue,
                "display": identifierValue
              },*/
              "subject": {
                "resource": "Patient",
                "identifer": {
                  "system": this.codingSystem,
                  "value": identifierValue
                }
              },
              "code": {
                "coding": [{
                  "system": this.codingSystem,
                  "code": itemKey,
                  "display": itemKey
                }]
              },
              "valueQuantity": valueQuantity,
              "valueString": valueString,
              "valueBoolean": valueString,
            };
            //console.log(observationData)
            //await this.createFhirResource(observationData, "Observation")
          }
        }
      }
    }
  },
};
</script>



