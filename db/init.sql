-- Criar a tabela pacientes_acupuntura
CREATE TABLE IF NOT EXISTS public.pacientes_acupuntura (
    cpf VARCHAR(11) NOT NULL,
    nome VARCHAR(255) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    complemento_endereco VARCHAR(255),
    bairro VARCHAR(100) NOT NULL,
    cep VARCHAR(8) NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    data_nascimento DATE NOT NULL,
    profissao VARCHAR(100) NOT NULL,
    sexo VARCHAR(50) NOT NULL CHECK (sexo IN ('Masculino', 'Feminino', 'Outro')),
    foto_paciente VARCHAR(100)
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pacientes_acupuntura_cpf_check CHECK (LENGTH(cpf) = 11),
    CONSTRAINT pacientes_acupuntura_pkey PRIMARY KEY (cpf)
);

-- Criar a tabela prontuario_acupuntura
CREATE TABLE IF NOT EXISTS public.prontuario_acupuntura (
    id SERIAL NOT NULL,
    cpf VARCHAR(11) NOT NULL,
    queixas_principais TEXT,
    sintomas_detalhados TEXT,
    intensidade_dor_eva INTEGER CHECK (intensidade_dor_eva BETWEEN 0 AND 10),
    medicamentos_atuais TEXT,
    historico_saude_pai TEXT,
    historico_familia_paterna TEXT,
    historico_saude_mae TEXT,
    historico_familia_materna TEXT,
    quantidade_qualidade_alimentos TEXT,
    horarios_refeicoes TEXT,
    condicoes_alimentares TEXT,
    preferencias_alimentares TEXT,
    apetite_paladar TEXT,
    problemas_digestivos TEXT,
    quantidade_ingestao_liquidos TEXT,
    sede_frequencia_intensidade TEXT,
    padroes_sono TEXT,
    frequencia_calafrios TEXT,
    padroes_transpiracao TEXT,
    historico_febre TEXT,
    sensibilidade_calor_frio TEXT,
    caracteristicas_fezes TEXT,
    caracteristicas_urina TEXT,
    menarca_menstruacao TEXT,
    menopausa TEXT,
    problemas_ginecologicos TEXT,
    problemas_urinarios TEXT,
    atividade_sexual TEXT,
    problemas_respiratorios TEXT,
    problemas_cardiovasculares TEXT,
    problemas_endocrinos TEXT,
    problemas_neurologicos TEXT,
    problemas_emocionais_infancia TEXT,
    problemas_emocionais_adolescencia TEXT,
    problemas_emocionais_adulto_jovem TEXT,
    problemas_emocionais_adulto TEXT,
    problemas_emocionais_idoso TEXT,
    problemas_osteomusculares TEXT,
    problemas_dermatologicos_alergias TEXT,
    pratica_lazer_exercicios TEXT,
    observacoes_cabelos TEXT,
    observacoes_olhos TEXT,
    observacoes_ouvidos TEXT,
    observacoes_nariz TEXT,
    observacoes_boca_labios_dentes TEXT,
    observacoes_pele TEXT,
    observacoes_expressao_rosto TEXT,
    descricao_lingua TEXT,
    mtc_vesicula_biliar TEXT,
    mtc_rim TEXT,
    mtc_bexiga TEXT,
    mtc_intestinos TEXT,
    mtc_estomago TEXT,
    mtc_baco TEXT,
    mtc_pulmao TEXT,
    mtc_coracao TEXT,
    palpacao_cabeca_pescoco TEXT,
    palpacao_maos_pes TEXT,
    auscultacao_olfacao TEXT,
    pressao_arterial TEXT,
    caracteristicas_voz TEXT,
    padrao_resinquira TEXT,
    caracteristicas_tosse TEXT,
    solucos_eructacoes TEXT,
    caracteristicas_halito TEXT,
    observacoes_excrecoes_secrecoes TEXT,
    outras_informacoes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT prontuario_acupuntura_cpf_check CHECK (LENGTH(cpf) = 11),
    CONSTRAINT prontuario_acupuntura_pkey PRIMARY KEY (id),
    CONSTRAINT prontuario_acupuntura_cpf_fkey FOREIGN KEY (cpf) REFERENCES public.pacientes_acupuntura (cpf)
);

-- Criar a tabela consultas
CREATE TABLE IF NOT EXISTS public.consultas (
    id SERIAL NOT NULL,
    cpf VARCHAR(11) NOT NULL,
    prontuario_id INTEGER NOT NULL,
    data_consulta DATE NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT consultas_cpf_check CHECK (LENGTH(cpf) = 11),
    CONSTRAINT consultas_pkey PRIMARY KEY (id),
    CONSTRAINT consultas_cpf_fkey FOREIGN KEY (cpf) REFERENCES public.pacientes_acupuntura (cpf),
    CONSTRAINT consultas_prontuario_id_fkey FOREIGN KEY (prontuario_id) REFERENCES public.prontuario_acupuntura (id)
);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_updated_at_pacientes
BEFORE UPDATE ON public.pacientes_acupuntura
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_update_updated_at_prontuario
BEFORE UPDATE ON public.prontuario_acupuntura
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_update_updated_at_consultas
BEFORE UPDATE ON public.consultas
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Inserir dados de teste
INSERT INTO public.pacientes_acupuntura (
    cpf, nome, endereco, bairro, cep, telefone, data_nascimento, profissao, sexo
) VALUES (
    '12345678901', 'João Silva', 'Rua das Flores, 123', 'Vila Mariana', '04101000', '(11) 99999-9999', '1985-05-20', 'Médico', 'Masculino'
) ON CONFLICT (cpf) DO NOTHING;

INSERT INTO public.prontuario_acupuntura (
    cpf, queixas_principais, intensidade_dor_eva, descricao_lingua
) VALUES (
    '12345678901', 'Dor lombar crônica', 6, 'Língua vermelha com saburra branca'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO public.consultas (
    cpf, prontuario_id, data_consulta, observacoes
) VALUES (
    '12345678901', 1, '2025-07-21', 'Consulta inicial, paciente relata melhora após primeira sessão'
) ON CONFLICT (id) DO NOTHING;