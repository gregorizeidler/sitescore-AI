from typing import Dict, Tuple, List
from .features import normalize

WEIGHTS = {
    # EXISTENTES
    "restaurante": {
        "flow_kde": 0.35,
        "transit": 0.20,
        "offices": 0.25,
        "mix": 0.10,
        "competition": -0.20,
    },
    "academia": {
        "parks": 0.25,
        "transit": 0.15,
        "flow_kde": 0.20,
        "schools": 0.10,
        "competition": -0.20,
        "mix": 0.10,
    },
    "varejo_moda": {
        "flow_kde": 0.30,
        "offices": 0.20,
        "transit": 0.20,
        "mix": 0.15,
        "competition": -0.25,
    },
    
    # NOVOS - ALIMENTAÇÃO
    "cafeteria": {
        "offices": 0.30,
        "transit": 0.25,
        "flow_kde": 0.25,
        "mix": 0.10,
        "competition": -0.15,
    },
    "padaria": {
        "flow_kde": 0.35,
        "transit": 0.15,
        "offices": 0.15,
        "schools": 0.10,
        "mix": 0.20,
        "competition": -0.20,
    },
    "lanchonete": {
        "flow_kde": 0.30,
        "transit": 0.25,
        "offices": 0.20,
        "schools": 0.10,
        "mix": 0.15,
        "competition": -0.18,
    },
    "mercado": {
        "flow_kde": 0.20,
        "transit": 0.20,
        "offices": 0.05,
        "schools": 0.05,
        "mix": 0.15,
        "competition": -0.30,
    },
    
    # NOVOS - SERVIÇOS
    "farmacia": {
        "flow_kde": 0.25,
        "transit": 0.20,
        "offices": 0.10,
        "schools": 0.05,
        "mix": 0.15,
        "competition": -0.25,
    },
    "pet_shop": {
        "parks": 0.30,
        "flow_kde": 0.15,
        "transit": 0.10,
        "mix": 0.15,
        "competition": -0.20,
    },
    "lavanderia": {
        "offices": 0.25,
        "transit": 0.15,
        "flow_kde": 0.15,
        "mix": 0.10,
        "competition": -0.30,
    },
    "salao_beleza": {
        "flow_kde": 0.25,
        "offices": 0.20,
        "transit": 0.15,
        "mix": 0.20,
        "competition": -0.25,
    },
    
    # NOVOS - VAREJO ESPECIALIZADO
    "livraria": {
        "schools": 0.25,
        "offices": 0.20,
        "transit": 0.20,
        "flow_kde": 0.20,
        "mix": 0.20,
        "competition": -0.20,
    },
    "coworking": {
        "offices": 0.30,
        "transit": 0.30,
        "flow_kde": 0.15,
        "mix": 0.25,
        "competition": -0.15,
    },
    "eletronicos": {
        "flow_kde": 0.25,
        "offices": 0.20,
        "transit": 0.25,
        "mix": 0.20,
        "competition": -0.25,
    },
    
    # NOVOS - ENTRETENIMENTO
    "bar": {
        "flow_kde": 0.30,
        "transit": 0.25,
        "offices": 0.15,
        "mix": 0.30,
        "competition": -0.20,
    },
    "cinema": {
        "flow_kde": 0.25,
        "transit": 0.30,
        "offices": 0.10,
        "mix": 0.35,
        "competition": -0.35,
    },
    "hotel": {
        "transit": 0.30,
        "flow_kde": 0.15,
        "offices": 0.15,
        "mix": 0.25,
        "parks": 0.10,
        "competition": -0.25,
    },
}

CAPS = {
    "competition": 50,
    "offices": 300,
    "schools": 20,
    "parks": 10,
    "transit": 40,
    "flow_kde": 50,
    "mix": 1.0,
}

def compute_score(business_type: str, raw_features: Dict[str, float]) -> Tuple[float, List[Dict], str]:
    w = WEIGHTS[business_type]
    feats_norm = {k: (raw_features.get(k, 0.0) if k == "mix" else normalize(raw_features.get(k, 0.0), CAPS.get(k, 1.0)))
                  for k in set(CAPS.keys()) | set(raw_features.keys())}
    contributions = []; total = 0.0
    for k, weight in w.items():
        v = feats_norm.get(k, 0.0)
        contrib = v * weight
        total += contrib
        contributions.append({
            "name": k,
            "value": raw_features.get(k, 0.0),
            "weight": weight,
            "contribution": contrib,
            "description": f"{k} (norm={v:.2f}) com peso {weight:+.2f}"
        })
    score = max(0.0, min(100.0, (total + 1) * 50))
    
    # Gerar explicação detalhada e contextualizada
    explanation = generate_detailed_explanation(business_type, raw_features, contributions, score)
    
    return score, contributions, explanation


def generate_detailed_explanation(business_type: str, raw_features: Dict[str, float], contributions: List[Dict], score: float) -> str:
    """
    Gera uma explicação detalhada e contextualizada da análise,
    descrevendo o que foi encontrado e os motivos do score.
    """
    paragraphs = []
    
    # Introdução com score
    if score >= 80:
        intro = f"🎯 **Localização Excelente** (Score: {score:.0f}/100)"
        intro_text = "Esta é uma localização muito promissora para o seu negócio, com diversos fatores positivos."
    elif score >= 60:
        intro = f"✅ **Localização Boa** (Score: {score:.0f}/100)"
        intro_text = "Esta localização apresenta boas condições para o negócio, com pontos positivos que superam os desafios."
    elif score >= 40:
        intro = f"⚠️ **Localização Razoável** (Score: {score:.0f}/100)"
        intro_text = "Esta localização tem potencial, mas apresenta alguns desafios que devem ser considerados."
    else:
        intro = f"❌ **Localização Desafiadora** (Score: {score:.0f}/100)"
        intro_text = "Esta localização apresenta diversos desafios significativos para o tipo de negócio escolhido."
    
    paragraphs.append(f"{intro}\n\n{intro_text}")
    
    # Análise de concorrência
    competition_count = int(raw_features.get('competition', 0))
    if competition_count > 0:
        if competition_count >= 20:
            comp_text = f"🏢 **Alta Concorrência:** Identificamos **{competition_count} concorrentes** no raio de 1km. Esta é uma área com forte presença do segmento, o que pode indicar demanda estabelecida, mas também maior competição por clientes."
        elif competition_count >= 10:
            comp_text = f"🏢 **Concorrência Moderada:** Encontramos **{competition_count} concorrentes** na região. Há competição, mas ainda existe espaço para diferenciação e conquista de mercado."
        elif competition_count >= 5:
            comp_text = f"🏢 **Concorrência Baixa:** Apenas **{competition_count} concorrentes** foram identificados. Isto pode representar uma oportunidade em mercado pouco saturado."
        else:
            comp_text = f"🏢 **Pouquíssima Concorrência:** Somente **{competition_count} concorrente(s)** na área. Mercado com baixa saturação, podendo indicar demanda não atendida ou área pouco comercial."
        paragraphs.append(comp_text)
    
    # Análise de transporte
    transit_count = int(raw_features.get('transit', 0))
    if transit_count > 0:
        if transit_count >= 10:
            transit_text = f"🚌 **Excelente Acesso ao Transporte:** A localização conta com **{transit_count} pontos de transporte público** próximos (estações de metrô, pontos de ônibus). Isto facilita muito o acesso de clientes e funcionários."
        elif transit_count >= 5:
            transit_text = f"🚌 **Bom Acesso ao Transporte:** **{transit_count} opções de transporte público** foram identificadas na região, garantindo mobilidade adequada para clientes."
        elif transit_count >= 2:
            transit_text = f"🚌 **Acesso Moderado ao Transporte:** **{transit_count} pontos de transporte** disponíveis, oferecendo alguma conectividade com outras regiões."
        else:
            transit_text = f"🚌 **Acesso Limitado ao Transporte:** Apenas **{transit_count} opção** de transporte público próxima. Considere se o público-alvo tem acesso a veículo próprio."
        paragraphs.append(transit_text)
    
    # Análise de escritórios (fluxo corporativo)
    offices_count = int(raw_features.get('offices', 0))
    if offices_count > 0:
        if offices_count >= 50:
            office_text = f"🏢 **Região Corporativa:** Mapeamos **{offices_count} escritórios** na área. Excelente para negócios que atendem público corporativo (horário comercial, almoço executivo, etc)."
        elif offices_count >= 20:
            office_text = f"🏢 **Presença Corporativa:** **{offices_count} escritórios** identificados, gerando fluxo de profissionais durante horário comercial."
        elif offices_count >= 5:
            office_text = f"🏢 **Alguns Escritórios:** **{offices_count} escritórios** na região, oferecendo algum potencial de clientes corporativos."
    
    # Análise de escolas (fluxo familiar)
    schools_count = int(raw_features.get('schools', 0))
    if schools_count > 0:
        if schools_count >= 10:
            school_text = f"🏫 **Muitas Escolas:** Há **{schools_count} instituições de ensino** próximas, gerando fluxo constante de famílias e estudantes nos horários de entrada/saída."
        elif schools_count >= 5:
            school_text = f"🏫 **Presença de Escolas:** **{schools_count} escolas** na área, trazendo movimento familiar para a região."
        elif schools_count >= 2:
            school_text = f"🏫 **Algumas Escolas:** **{schools_count} escolas** identificadas, com potencial de fluxo nos horários escolares."
    
    # Análise de parques (lazer e bem-estar)
    parks_count = int(raw_features.get('parks', 0))
    if parks_count > 0:
        if parks_count >= 5:
            park_text = f"🌳 **Área Verde:** A região possui **{parks_count} parques e áreas verdes**, indicando área com foco em qualidade de vida e lazer."
        elif parks_count >= 2:
            park_text = f"🌳 **Espaços Verdes:** **{parks_count} áreas verdes** próximas, agregando valor à localização."
    
    # Análise de mix (diversidade)
    mix_score = raw_features.get('mix', 0)
    if mix_score > 0.7:
        mix_text = f"🎨 **Alta Diversidade:** A região tem grande variedade de estabelecimentos e serviços (mix score: {mix_score:.2f}), indicando área comercial consolidada e movimentada."
    elif mix_score > 0.4:
        mix_text = f"🎨 **Boa Diversidade:** Variedade moderada de comércios e serviços (mix score: {mix_score:.2f}), caracterizando área comercial em desenvolvimento."
    
    # Análise de fluxo (KDE)
    flow_score = raw_features.get('flow_kde', 0)
    if flow_score > 50:
        flow_text = f"👥 **Alto Fluxo de Pessoas:** A análise de densidade indica movimento intenso de pedestres na área (score: {flow_score:.0f}), sugerindo boa visibilidade e tráfego de potenciais clientes."
    elif flow_score > 20:
        flow_text = f"👥 **Fluxo Moderado:** Movimento médio de pessoas detectado (score: {flow_score:.0f}), com potencial de visibilidade."
    
    # Adicionar textos gerados ao relatório
    for text_var in ['comp_text', 'transit_text', 'office_text', 'school_text', 'park_text', 'mix_text', 'flow_text']:
        if text_var in locals():
            paragraphs.append(locals()[text_var])
    
    # Conclusão com recomendação
    top_factors = sorted(contributions, key=lambda c: abs(c["contribution"]), reverse=True)[:3]
    top_names = [f["name"] for f in top_factors if abs(f["contribution"]) > 0.1]
    
    if score >= 70:
        conclusion = f"💡 **Recomendação:** Localização recomendada! Os principais fatores positivos são: **{', '.join(top_names)}**. Considere visitar o local em diferentes horários para validar o movimento."
    elif score >= 50:
        conclusion = f"💡 **Recomendação:** Localização viável, mas analise cuidadosamente os custos vs. potencial. Principais fatores: **{', '.join(top_names)}**. Considere estratégias de diferenciação."
    else:
        conclusion = f"💡 **Recomendação:** Avalie outras opções ou prepare estratégias específicas para superar os desafios. Fatores críticos: **{', '.join(top_names)}**."
    
    paragraphs.append(conclusion)
    
    return "\n\n".join(paragraphs)
