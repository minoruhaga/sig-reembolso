from django.core.exceptions import ValidationError


class SigReembolsoDomainError(ValidationError):
    """
    Exceção base para violações de regras de negócio e invariantes contábeis do SIG-Reembolso.

    - O que faz: Unifica os erros semânticos de domínio em uma hierarquia própria compatível com o Django.
    - Como faz: Herda diretamente de `django.core.exceptions.ValidationError` preservando suporte a mensagens,
      códigos de erro e integração nativa com `Model.clean()` e `ModelForm`.
    - Qual finalidade atende: Facilita o tratamento explícito de regras contábeis (RN01 a RN06) nas views e
      serviços sem quebrar a retrocompatibilidade com testes que capturam `ValidationError`.
    """


class ComprovanteObrigatorioError(SigReembolsoDomainError):
    """
    Exceção disparada quando há tentativa de tramitar uma despesa sem comprovante fiscal válido (RN01).

    - O que faz: Sinaliza especificamente a ausência ou invalidade do anexo fiscal obrigatório.
    - Como faz: Especializa `SigReembolsoDomainError` mantendo compatibilidade com `ValidationError`.
    - Qual finalidade atende: Garante a aplicação explícita da RN01 na submissão de despesas de campo do AG VII.
    """


class TransicaoStatusInvalidaError(SigReembolsoDomainError):
    """
    Exceção disparada quando uma operação viola a máquina de estados finita da Despesa.

    - O que faz: Indica que o estado atual do lançamento não permite a transição solicitada.
    - Como faz: Especializa `SigReembolsoDomainError` para uso em métodos de estado e serviços transacionais.
    - Qual finalidade atende: Preserva a integridade do fluxo `RASCUNHO -> ENVIADO -> APROVADO -> PAGO`.
    """


class SegregacaoFuncoesError(SigReembolsoDomainError):
    """
    Exceção disparada quando um tesoureiro tenta analisar ou liquidar uma despesa própria (RN03).

    - O que faz: Bloqueia ações de aprovação, reprovação ou liquidação em conflito de interesses.
    - Como faz: Especializa `SigReembolsoDomainError` mantendo captura padrão via `ValidationError`.
    - Qual finalidade atende: Sustenta a governança financeira e auditoria estrita da RN03 na Tesouraria.
    """


class JustificativaRejeicaoObrigatoriaError(SigReembolsoDomainError):
    """
    Exceção disparada ao rejeitar uma despesa sem informar parecer textual obrigatório (RN04).

    - O que faz: Sinaliza ausência de justificativa na reprovação de comprovantes na triagem.
    - Como faz: Especializa `SigReembolsoDomainError` para validação clara em serviços e formulários.
    - Qual finalidade atende: Assegura transparência ao coordenador de campo para corrigir despesas recusadas.
    """


class ImutabilidadeDespesaError(SigReembolsoDomainError):
    """
    Exceção disparada ao tentar alterar ou excluir uma despesa já aprovada ou liquidada (RN05).

    - O que faz: Protege lançamentos homologados contra adulteração de valor, pasta, data, anexo ou status.
    - Como faz: Especializa `SigReembolsoDomainError` em conformidade com as validações de modelo e serviço.
    - Qual finalidade atende: Garante lastro contábil inalterável para a prestação de contas do GE Caramuru.
    """


class PermissaoNegadaDominioError(SigReembolsoDomainError):
    """
    Exceção disparada quando um usuário sem o papel necessário tenta executar uma ação restrita (RF01).

    - O que faz: Indica falha de autorização no nível de regras de domínio e serviços (RBAC).
    - Como faz: Especializa `SigReembolsoDomainError` desacoplando validações de domínio da camada HTTP.
    - Qual finalidade atende: Reforça o controle de acesso baseado em papéis entre Coordenador, Tesoureiro e Admin.
    """
