class ProblemAnswerInfo:
    def __init__(self, problem, answer, answer_list):
        self._problem = problem
        self._answer = answer
        self._answer_list = answer_list

    def get_problem(self):
        return self._problem

    def get_answer(self):
        return self._answer

    def get_answer_list(self):
        return self._answer_list

    def __str__(self):
        return f"[ProblemAnswerInfo] problem={self._problem}, answer={self._answer}, answer_list={self._answer_list}"
