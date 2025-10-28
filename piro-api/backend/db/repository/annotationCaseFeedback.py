from db.models.AnnotationCaseFeedback import AnnotationCaseFeedback
from exception.data_exception import DataException
from sqlalchemy import text, desc
from sqlalchemy.orm import Session
from viewmodel.annotationCaseFeedback import AnnotationCaseFeedbackVMCreate
from db.dict2Class import dict2Class


def create_new_feedback(
    input: AnnotationCaseFeedbackVMCreate, userId: int, user: str, db: Session
):
    feedback = AnnotationCaseFeedback(
        AnnotationConfigurationId=input.annotationConfigurationId,
        CaseId=input.caseid,
        UserId=userId,
        Feedback=input.feedback,
        Comment=input.comment,
        IsReviewed=False,
        CreateBy=user,
    )
    db.add(feedback)
    db.commit()
    return feedback


def update_review(
    input: AnnotationCaseFeedbackVMCreate, user: str, db: Session
):
    feedback = (
        db.query(AnnotationCaseFeedback)
        .filter(
            AnnotationCaseFeedback.AnnotationCaseFeedbackId
            == input.annotationCaseFeedbackId
        )
        .first()
    )
    if feedback is not None:
        feedback.IsReviewed = True
        feedback.UpdatedBy = user
        db.commit()
    else:
        raise DataException("Annotation Feedback does not exist")
    return feedback


def pending_review(db: Session):
    feedback = (
        db.query(AnnotationCaseFeedback)
        .filter(AnnotationCaseFeedback.Feedback == -1)
        .filter(AnnotationCaseFeedback.IsReviewed == False)  # noqa
        .count()
    )

    return True if feedback > 0 else False


def search_feedback(
    caseid: int,
    casenum: str,
    annotationConfigurationId: int,
    feedback: int,
    pending: bool,
    db: Session,
):
    filter = ""
    if annotationConfigurationId != -1:
        filter = f"{filter} AND F.AnnotationConfigurationId = {annotationConfigurationId}"

    if caseid != -1:
        filter = f"{filter} AND F.CaseId = {caseid}"

    if casenum != "":
        filter = f"{filter} AND C.CaseNumber like '%{casenum}%'"

    if pending == True:  # noqa
        filter = f"{filter} AND F.IsReviewed = 0 AND Feedback = -1"

    if feedback != 0:
        filter = f"{filter} AND F.Feedback = {feedback}"

    sql = text(
        "select F.AnnotationCaseFeedbackId, F.AnnotationConfigurationId, F.CaseId, C.CaseNumber, "
        + "F.Feedback, F.Comment, F.IsReviewed, F.CreateDate, dbo.F_FullName(U.FirstName, '', U.LastName) UserName, "
        + "AC.DisplayText AnnotationConfigurationName  from [dbo].[AnnotationCaseFeedback] F "
        + "join [dbo].[Case] C on F.CaseId = C.CaseId "
        + "join [dbo].[User] U on F.UserId = U.UserId "
        + "join [dbo].[AnnotationConfiguration] AC on F.AnnotationConfigurationId = AC.AnnotationConfigurationId Where 1 = 1 "
        + f"{filter} "
        + "Order by F.AnnotationCaseFeedbackId desc"
    )

    rs = db.execute(sql)
    result = []
    for row in rs:
        item = dict2Class(
            {
                "AnnotationCaseFeedbackId": row[0],
                "AnnotationConfigurationId": row[1],
                "CaseId": row[2],
                "CaseNumber": row[3],
                "Feedback": row[4],
                "Comment": row[5],
                "IsReviewed": row[6],
                "CreateDate": row[7],
                "UserName": row[8],
                "AnnotationConfigurationName": row[9],
            }
        )
        result.append(item)
    return result


def feedback_data(caseId: int, configId: int, userId: int, db: Session):
    # Positive votes
    positiveVoteCount = (
        db.query(AnnotationCaseFeedback)
        .filter(AnnotationCaseFeedback.CaseId == caseId)
        .filter(AnnotationCaseFeedback.AnnotationConfigurationId == configId)
        .filter(AnnotationCaseFeedback.Feedback == 1)
        .count()
    )

    # Negative votes
    negativeVoteCount = (
        db.query(AnnotationCaseFeedback)
        .filter(AnnotationCaseFeedback.CaseId == caseId)
        .filter(AnnotationCaseFeedback.AnnotationConfigurationId == configId)
        .filter(AnnotationCaseFeedback.Feedback == -1)
        .count()
    )

    # User latest vote
    latestVoteData = (
        db.query(AnnotationCaseFeedback)
        .filter(AnnotationCaseFeedback.CaseId == caseId)
        .filter(AnnotationCaseFeedback.AnnotationConfigurationId == configId)
        .filter(AnnotationCaseFeedback.UserId == userId)
        .order_by(desc(AnnotationCaseFeedback.AnnotationCaseFeedbackId))
        .first()
    )
    latestVote = 0
    if latestVoteData is None:
        latestVote = 0
    else:
        latestVote = latestVoteData.Feedback

    return dict2Class(
        {
            "PostiveVoteCount": positiveVoteCount,
            "NegativeVoteCount": negativeVoteCount,
            "MyVote": latestVote,
        }
    )
