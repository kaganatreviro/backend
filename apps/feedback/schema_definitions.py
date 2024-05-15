from drf_spectacular.utils import (OpenApiExample, extend_schema_serializer)

feedback_schema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Feedback List Success",
            description="Successful listings of Feedbacks",
            value=[
                {
                    "id": 1,
                    "user": "client@mail.com",
                    "created_at": "2024-05-15T13:08:41.489420+06:00",
                    "establishment": 1,
                    "text": "Text of feedback"
                },
                {
                    "id": 2,
                    "user": "other_client@mail.com",
                    "created_at": "2024-05-15T13:11:11.105170+06:00",
                    "establishment": 1,
                    "text": "Text of feedback"
                },
            ],
            response_only=True,
        ),
        OpenApiExample(
            name="Feedback Retrieve Success",
            description="Successful retrieve of Feedback",
            value={
                "id": 1,
                "user": "client@mail.com",
                "created_at": "2024-05-07T14:49:37.914129+06:00",
                "establishment": 1,
                "text": "Text of feedback"
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Feedback Update Success",
            description="Successful update of Feedback",
            value={
                "id": 1,
                "user": "client@mail.com",
                "created_at": "2024-05-07T14:49:37.914129+06:00",
                "establishment": 1,
                "text": "Text of feedback"
            },
            response_only=True,
        ),
    ]
)

feedback_answer_schema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Feedback's Answers List Success",
            description="Successful listings of Feedback's Answers",
            value=[
                {
                    "id": 1,
                    "feedback": 1,
                    "user": "admin@mail.com",
                    "created_at": "2024-05-15T13:39:36.660065+06:00",
                    "text": "Text of feedback answer"
                },
                {
                    "id": 2,
                    "feedback": 1,
                    "user": "admin@mail.com",
                    "created_at": "2024-05-15T15:57:42.598603+06:00",
                    "text": "Text of feedback answer"
                }
            ],
            response_only=True,
        ),
        OpenApiExample(
            name="Feedback's Answer Retrieve Success",
            description="Successful retrieve of Feedback's Answer",
            value={
                "id": 1,
                "feedback": 1,
                "user": "admin@mail.com",
                "created_at": "2024-05-07T14:52:54.661184+06:00",
                "text": "Text of feedback answer"
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Feedback's Answer Update Success",
            description="Successful update of Feedback's Answer",
            value={
                "id": 1,
                "feedback": 1,
                "user": "admin@mail.com",
                "created_at": "2024-05-07T14:52:54.661184+06:00",
                "text": "Text of feedback answer"
            },
            response_only=True,
        ),
    ]
)
