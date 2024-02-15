<template>
  <router-view />
</template>

<script lang="ts" setup>
import { onMounted } from 'vue';
//import FHIR from 'your-fhir-library'; // Import your FHIR library
import FHIR from "fhirclient";
onMounted(async () => {
  const client = FHIR.client("http://localhost:8080/fhir");
  const bundle = await client.request("Patient");
  console.log(bundle);
 /*const patientData = {
        "resourceType": "Patient",
        "id": "testId",
        "name": [{
          "family": "Doe",
          "given": ["John"]
        }],
        "gender": "male",
        "birthDate": "1960-0143-03"
      }
      const client = FHIR.client("http://localhost:8080/fhir");
      const createBundle = await client.create(patientData);
      console.log(createBundle);*/
});
</script>
