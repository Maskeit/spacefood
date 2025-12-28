// 1. Tomar el texto completo de Gemini
const rawText = $input.first().json.content.parts[0].text;
// 2. Parsear el JSON limpio
const data = JSON.parse(rawText);

// PROVEEDORES
const proveedores = data.proveedores?.map((p) => ({
  id_fiscal: p.id_fiscal || "",
  nombre: p.nombre || "",
  domicilio: p.domicilio || "",
})) || [];

// Extraer facturas correctamente (son objetos con propiedad "numero")
const todasLasFacturas = data.proveedores?.flatMap((p) => 
  p.facturas?.map((f) => f.numero) || []
) || [];
const facturasNumero = todasLasFacturas.join(", ");

// Extraer fechas de facturas
const todasLasFechasFacturas = data.proveedores?.flatMap((p) => 
  p.facturas?.map((f) => f.fecha) || []
) || [];
const fechasFactura = todasLasFechasFacturas.join(", ");

// MERCANCIAS (PARTIDAS)
const mercancias = data.partidas?.map((p) => ({
  partida: p.numero_secuencia || "",
  descripcion: p.descripcion || "",
  clasificacion_arancelaria: p.fraccion_arancelaria || "",
  cantidad_umc: p.cantidad_umc || "",
  pais_produccion: p.pais_origen || "",
  pais_procedencia: p.pais_vendedor || "",
})) || [];

// Extraer número de patente (4 dígitos centrales del pedimento)
const numPedimento = data.encabezado?.numero_pedimento || "";
const partesPedimento = numPedimento.split(" ");
const patente = partesPedimento[2] || "";

// Calcular totales de incrementables
const fletes = parseFloat(data.valores_globales?.fletes || 0);
const seguros = parseFloat(data.valores_globales?.seguros || 0);
const fletesSeguros = fletes + seguros;

const embalajes = parseFloat(data.valores_globales?.embalajes || 0);
const otrosIncrementables = parseFloat(data.valores_globales?.otros_incrementables || 0);
const cargaDescarga = embalajes + otrosIncrementables;

const totalIncrementables = fletesSeguros + cargaDescarga;

const precioPagado = data.valores_globales?.precio_pagado || "";

// Fechas
const fechaPedimento = data.encabezado?.fechas?.entrada || "";

// Determinar si hay más de un pedimento (si el total de partidas > 1 podrías tener múltiples pedimentos)
// Por ahora, asumimos que es un solo pedimento, el campo "mas" se marca vacío
// Si en el futuro necesitas detectar múltiples pedimentos, ajusta esta lógica
const tieneMasPedimentos = false; // Cambiar según lógica de negocio

// SALIDA FINAL según example.json
return [
  {
    json: {
      metadatos: {},
      importador: {
        importador_nombre: data.importador_exportador?.nombre || "",
        importador_domicilio: data.importador_exportador?.domicilio || "",
        importador_rfc: data.importador_exportador?.rfc || "",
        pedimento: numPedimento,
        fecha_pedimento: fechaPedimento,
        num_factura: facturasNumero,
        fecha_factura: fechasFactura,
      },
      proveedores,
      mercancias,
      determinacion_metodo: {
        compraventa: "s",
        vinculadas: "n",
        restricciones: "n",
        contraprestaciones: "n",
        regalias: "n",
      },
      precio_pagado: {
        precio_pagado: precioPagado,
        indirectos: "0",
        total: precioPagado,
      },
      incrementables: {
        comisiones: "0",
        fletes_seguros: fletesSeguros.toString(),
        carga_descarga: cargaDescarga.toString(),
        materiales_aportados: "0",
        tecnologia_aportada: "0",
        regalias: "0",
        reversiones: "0",
        total: totalIncrementables.toString(),
      },
      no_incrementables: {
        gastos_no_relacionados: "0",
        fletes_seguros: "0",
        gastos_de_construccion: "0",
        armado: "0",
        contribuciones: "0",
        dividendos: "0",
        total: "0",
      },
      aduana: {
        precio_pagado: precioPagado,
        ajustes_incrementables: totalIncrementables.toString(),
      },
      pedimento: {
        num_pedimento: numPedimento,
        fecha_pedimento: fechaPedimento,
        factura_num: facturasNumero,
        fecha_factura: fechasFactura,
        emision_factura: "",
        tipo_factura: "x",
        mas: tieneMasPedimentos ? "x" : "",
      },
      suscrito: {
        representante: "Jaime Mayagoitia Orozco",
        rfc_legal: "MAOJ640430AR7",
        fecha_pedimento: fechaPedimento,
      },
      num_patente: {
        patente: patente,
      },
    },
  },
];