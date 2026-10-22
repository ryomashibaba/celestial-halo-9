// Run after analyze.cjs has completed. Requires the established sharp package.
// Example: node render-previews.cjs <absolute-path-to-sharp-package>
const path=require('path');
const sharp=require(process.argv[2]||'sharp');
(async()=>{
 for(const id of ['N1','N2','N3','C3'])for(const kind of ['six-views','sections']){
  const base=path.join(__dirname,id+'-'+kind);
  await sharp(base+'.svg').png({palette:true,colours:128,compressionLevel:9,effort:10}).toFile(base+'.png');
 }
 console.log('PNG diagnostic sheets generated from analytic-model SVGs.');
})().catch(e=>{console.error(e);process.exitCode=1;});
