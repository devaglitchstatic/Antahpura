import characterTemplate from '../../data/constitution/antahpura_character_template_v1.json';
import entryBlocks from '../../data/constitution/antahpura_entry_blocks_v1.json';
import kalas from '../../data/constitution/kalas_64_reference.json';
import disciplines from '../../data/constitution/disciplines.json';
import protocols from '../../data/constitution/protocol_engine.json';
import temples from '../../data/constitution/temples_occasions.json';
import monitoring from '../../data/constitution/monitoring_matrix_schema.json';
import sakshi from '../../data/characters/sakshi.json';\nimport mahaDeva from '../../data/characters/maha_deva.json';\nimport princess from '../../data/characters/princess_kuma_ree_rati.json';

export const constitution = {
  version: 'Constitution v1.0',
  template: characterTemplate,
  entryBlocks,
  kalas,
  disciplines,
  protocols,
  temples,
  monitoring,\n\n  characters: {\n    mahaDeva,\n    princess\n  },
  sakshi,

  getDiscipline(id: string) {
    return (disciplines as any).disciplines[id];
  },

  getTemple(id: string) {
    return (temples as any).temples[id];
  },

  getOccasion(id: string) {
    return (temples as any).occasions[id];
  },

  getMetric(id: string) {
    const groups = (monitoring as any);
    for (const key of ['physiological','emotional','relational','witness']) {
      if (groups[key] && groups[key][id]) return groups[key][id];
    }
    return null;
  }
};

export default constitution;
