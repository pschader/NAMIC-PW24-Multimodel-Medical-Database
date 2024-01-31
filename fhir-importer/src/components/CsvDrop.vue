<template>
  <v-container>
    <v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field label="Coding System" variant="solo"></v-text-field>
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
              <td>FHIR Ressource</td>
              <td>FHIR Field</td>
              <td>Action</td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="header in headers" :key="header.key">
              <td>{{ header.key }}</td>
              <td><v-combobox label="Ressource" v-model="mapping[header.key]['ressource']" :items="['Ignore', 'Observation', 'Patient']" variant="outlined" ></v-combobox></td>
              <td><v-combobox label="Field" v-model="mapping[header.key]['field']" :items="['Value', 'Subject']" variant="outlined" ></v-combobox></td>
              <td><v-combobox label="Action" v-model="mapping[header.key]['action']" :items="['Cast to Int', 'Subject']" variant="outlined" ></v-combobox></td>
            </tr>
          </tbody>
        </v-table>
      </v-col>
    </v-row>
    <v-row v-if="headers.length !== 0">
      <v-col cols="12">
        <v-textarea label="FHIR Ressources" variant="solo"></v-textarea>
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
export default {
  data() {
    return {
      items: [],
      headers: [],
      mapping: {},
    };
  },
  methods: {
    handleDrop(e) {
      const file = e.dataTransfer.files[0];
      this.parseCsv(file);
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
    onChange(e) {
      // for(var key in this.mapping) {
      //   const ressource = this.mapping[key]['ressource']
      //   const field = this.mapping[key]['field']
      //   console.log();
      // }
    }
  },
};
</script>
