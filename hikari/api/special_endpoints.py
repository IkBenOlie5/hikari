# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021 davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Special additional endpoints used by the REST API."""
from __future__ import annotations

__all__: typing.List[str] = [
    "CommandBuilder",
    "TypingIndicator",
    "GuildBuilder",
    "InteractionDeferredBuilder",
    "InteractionResponseBuilder",
    "InteractionMessageBuilder",
]

import abc
import typing

from hikari import undefined

if typing.TYPE_CHECKING:
    import types

    from hikari import channels
    from hikari import colors
    from hikari import embeds as embeds_
    from hikari import files
    from hikari import guilds
    from hikari import messages
    from hikari import permissions as permissions_
    from hikari import snowflakes
    from hikari import users
    from hikari import voices
    from hikari.api import entity_factory as entity_factory_
    from hikari.interactions import bases as base_interactions
    from hikari.interactions import commands
    from hikari.internal import data_binding
    from hikari.internal import time

    _T = typing.TypeVar("_T")


class TypingIndicator(abc.ABC):
    """Result type of `hikari.api.rest.RESTClient.trigger_typing`.

    This is an object that can either be awaited like a coroutine to trigger
    the typing indicator once, or an async context manager to keep triggering
    the typing indicator repeatedly until the context finishes.

    !!! note
        This is a helper class that is used by `hikari.api.rest.RESTClient`.
        You should only ever need to use instances of this class that are
        produced by that API.
    """

    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def __await__(self) -> typing.Generator[None, typing.Any, None]:
        ...

    @abc.abstractmethod
    async def __aenter__(self) -> None:
        ...

    @abc.abstractmethod
    async def __aexit__(
        self,
        exception_type: typing.Type[BaseException],
        exception: BaseException,
        exception_traceback: types.TracebackType,
    ) -> None:
        ...


class GuildBuilder(abc.ABC):
    """Result type of `hikari.api.rest.RESTClient.guild_builder`.

    This is used to create a guild in a tidy way using the HTTP API, since
    the logic behind creating a guild on an API level is somewhat confusing
    and detailed.

    !!! note
        This is a helper class that is used by `hikari.api.rest.RESTClient`.
        You should only ever need to use instances of this class that are
        produced by that API, thus, any details about the constructor are
        omitted from the following examples for brevity.

    Examples
    --------
    Creating an empty guild.

    ```py
    guild = await rest.guild_builder("My Server!").create()
    ```

    Creating a guild with an icon

    ```py
    from hikari.files import WebResourceStream

    guild_builder = rest.guild_builder("My Server!")
    guild_builder.icon = WebResourceStream("cat.png", "http://...")
    guild = await guild_builder.create()
    ```

    Adding roles to your guild.

    ```py
    from hikari.permissions import Permissions

    guild_builder = rest.guild_builder("My Server!")

    everyone_role_id = guild_builder.add_role("@everyone")
    admin_role_id = guild_builder.add_role("Admins", permissions=Permissions.ADMINISTRATOR)

    await guild_builder.create()
    ```

    !!! warning
        The first role must always be the `@everyone` role.

    !!! note
        If you call `add_role`, the default roles provided by discord will
        be created. This also applies to the `add_` functions for
        text channels/voice channels/categories.

    !!! note
        Functions that return a `hikari.snowflakes.Snowflake` do
        **not** provide the final ID that the object will have once the
        API call is made. The returned IDs are only able to be used to
        re-reference particular objects while building the guild format.

        This is provided to allow creation of channels within categories,
        and to provide permission overwrites.

    Adding a text channel to your guild.

    ```py
    guild_builder = rest.guild_builder("My Server!")

    category_id = guild_builder.add_category("My safe place")
    channel_id = guild_builder.add_text_channel("general", parent_id=category_id)

    await guild_builder.create()
    ```
    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the guild to create.

        Returns
        -------
        builtins.str
            The guild name.
        """

    @property
    @abc.abstractmethod
    def default_message_notifications(self) -> undefined.UndefinedOr[guilds.GuildMessageNotificationsLevel]:
        """Default message notification level that can be overwritten.

        If not overridden, this will use the Discord default level.

        Returns
        -------
        hikari.undefined.UndefinedOr[hikari.guilds.GuildMessageNotificationsLevel]
            The default message notification level, if overwritten.
        """  # noqa: D401 - Imperative mood

    @default_message_notifications.setter
    def default_message_notifications(
        self, default_message_notifications: undefined.UndefinedOr[guilds.GuildMessageNotificationsLevel], /
    ) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def explicit_content_filter_level(self) -> undefined.UndefinedOr[guilds.GuildExplicitContentFilterLevel]:
        """Explicit content filter level that can be overwritten.

        If not overridden, this will use the Discord default level.

        Returns
        -------
        hikari.undefined.UndefinedOr[hikari.guilds.GuildExplicitContentFilterLevel]
            The explicit content filter level, if overwritten.
        """

    @explicit_content_filter_level.setter
    def explicit_content_filter_level(
        self, explicit_content_filter_level: undefined.UndefinedOr[guilds.GuildExplicitContentFilterLevel], /
    ) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def icon(self) -> undefined.UndefinedOr[files.Resourceish]:
        """Guild icon to use that can be overwritten.

        If not overridden, the guild will not have an icon.

        Returns
        -------
        hikari.undefined.UndefinedOr[hikari.files.Resourceish]
            The guild icon to use, if overwritten.
        """

    @icon.setter
    def icon(self, icon: undefined.UndefinedOr[files.Resourceish], /) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def verification_level(self) -> undefined.UndefinedOr[typing.Union[guilds.GuildVerificationLevel, int]]:
        """Verification level required to join the guild that can be overwritten.

        If not overridden, the guild will use the default verification level for

        Returns
        -------
        hikari.undefined.UndefinedOr[typing.Union[hikari.guilds.GuildVerificationLevel, builtins.int]]
            The verification level required to join the guild, if overwritten.
        """

    @verification_level.setter
    def verification_level(
        self, verification_level: undefined.UndefinedOr[typing.Union[guilds.GuildVerificationLevel, int]], /
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def create(self) -> guilds.RESTGuild:
        """Send the request to Discord to create the guild.

        The application user will be added to this guild as soon as it is
        created. All IDs that were provided when building this guild will
        become invalid and will be replaced with real IDs.

        Returns
        -------
        hikari.guilds.RESTGuild
            The created guild.

        Raises
        ------
        hikari.errors.BadRequestError
            If any values set in the guild builder are invalid.
        hikari.errors.UnauthorizedError
            If you are unauthorized to make the request (invalid/missing token).
        hikari.errors.ForbiddenError
            If you are already in 10 guilds.
        hikari.errors.InternalServerError
            If an internal error occurs on Discord while handling the request.
        """

    @abc.abstractmethod
    def add_role(
        self,
        name: str,
        /,
        *,
        permissions: undefined.UndefinedOr[permissions_.Permissions] = undefined.UNDEFINED,
        color: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        colour: undefined.UndefinedOr[colors.Colorish] = undefined.UNDEFINED,
        hoist: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        mentionable: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a role.

        !!! warning
            The first role you create must always be the `@everyone` role.

        Parameters
        ----------
        name : builtins.str
            The role's name.

        Other Parameters
        ----------------
        permissions : hikari.undefined.UndefinedOr[hikari.permissions.Permissions]
            If provided, the permissions for the role.
        color : hikari.undefined.UndefinedOr[hikari.colors.Colorish]
            If provided, the role's color.
        colour : hikari.undefined.UndefinedOr[hikari.colors.Colorish]
            An alias for `color`.
        hoist : hikari.undefined.UndefinedOr[builtins.bool]
            If provided, whether to hoist the role.
        mentionable : hikari.undefined.UndefinedOr[builtins.bool]
            If provided, whether to make the role mentionable.
        reason : hikari.undefined.UndefinedOr[builtins.str]
            If provided, the reason that will be recorded in the audit logs.
            Maximum of 512 characters.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this role that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.

        Raises
        ------
        builtins.ValueError
            If you are defining the first role, but did not name it `@everyone`.
        builtins.TypeError
            If you specify both `color` and `colour` together or if you try to
            specify `color`, `colour`, `hoisted`, `mentionable` or `position` for
            the `@everyone` role.
        """

    @abc.abstractmethod
    def add_category(
        self,
        name: str,
        /,
        *,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a category channel.

        Parameters
        ----------
        name : builtins.str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the position of the category.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the category.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def add_text_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        topic: undefined.UndefinedOr[str] = undefined.UNDEFINED,
        rate_limit_per_user: undefined.UndefinedOr[time.Intervalish] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        nsfw: undefined.UndefinedOr[bool] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a text channel.

        Parameters
        ----------
        name : builtins.str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the position of the channel (relative to the
            category, if any).
        topic : hikari.undefined.UndefinedOr[builtins.str]
            If provided, the channels topic. Maximum 1024 characters.
        nsfw : hikari.undefined.UndefinedOr[builtins.bool]
            If provided, whether to mark the channel as NSFW.
        rate_limit_per_user : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the ammount of seconds a user has to wait
            before being able to send another message in the channel.
            Maximum 21600 seconds.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        category : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.channels.GuildCategory]]
            The category to create the channel under. This may be the
            object or the ID of an existing category.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def add_voice_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        video_quality_mode: undefined.UndefinedOr[typing.Union[channels.VideoQualityMode, int]] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedNoneOr[typing.Union[voices.VoiceRegion, str]],
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a voice channel.

        Parameters
        ----------
        name : builtins.str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        video_quality_mode: hikari.undefined.UndefinedOr[typing.Union[hikari.channels.VideoQualityMode, builtins.int]]
            If provided, the new video quality mode for the channel.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        region : hikari.undefined.UndefinedOr[typing.Union[hikari.voices.VoiceRegion, builtins.str]]
             If provided, the voice region to for this channel. Passing
             `builtins.None` here will set it to "auto" mode where the used
             region will be decided based on the first person who connects to it
             when it's empty.
        category : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.channels.GuildCategory]]
            The category to create the channel under. This may be the
            object or the ID of an existing category.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def add_stage_channel(
        self,
        name: str,
        /,
        *,
        parent_id: undefined.UndefinedOr[snowflakes.Snowflake] = undefined.UNDEFINED,
        bitrate: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        position: undefined.UndefinedOr[int] = undefined.UNDEFINED,
        permission_overwrites: undefined.UndefinedOr[
            typing.Collection[channels.PermissionOverwrite]
        ] = undefined.UNDEFINED,
        region: undefined.UndefinedNoneOr[typing.Union[voices.VoiceRegion, str]],
        user_limit: undefined.UndefinedOr[int] = undefined.UNDEFINED,
    ) -> snowflakes.Snowflake:
        """Create a stage channel.

        Parameters
        ----------
        name : builtins.str
            The channels name. Must be between 2 and 1000 characters.

        Other Parameters
        ----------------
        position : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the position of the channel (relative to the
            category, if any).
        user_limit : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the maximum users in the channel at once.
            Must be between 0 and 99 with 0 meaning no limit.
        bitrate : hikari.undefined.UndefinedOr[builtins.int]
            If provided, the bitrate for the channel. Must be
            between 8000 and 96000 or 8000 and 128000 for VIP
            servers.
        permission_overwrites : hikari.undefined.UndefinedOr[typing.Sequence[hikari.channels.PermissionOverwrite]]
            If provided, the permission overwrites for the channel.
        region : hikari.undefined.UndefinedOr[typing.Union[hikari.voices.VoiceRegion, builtins.str]]
             If provided, the voice region to for this channel. Passing
             `builtins.None` here will set it to "auto" mode where the used
             region will be decided based on the first person who connects to it
             when it's empty.
        category : hikari.undefined.UndefinedOr[hikari.snowflakes.SnowflakeishOr[hikari.channels.GuildCategory]]
            The category to create the channel under. This may be the
            object or the ID of an existing category.

        Returns
        -------
        hikari.snowflakes.Snowflake
            The dummy ID for this channel that can be used temporarily to refer
            to this object while designing the guild layout.

            When the guild is created, this will be replaced with a different
            ID.
        """


class InteractionResponseBuilder(abc.ABC):
    """Base class for all interaction response builders used in the interaction server."""

    @property
    @abc.abstractmethod
    def type(self) -> typing.Union[int, base_interactions.ResponseType]:
        """Return the type of this response.

        Returns
        -------
        typing.Union[builtins.int, hikari.interactions.bases.ResponseType]
            The type of response this is.
        """

    @abc.abstractmethod
    def build(self, entity_factory: entity_factory_.EntityFactory, /) -> data_binding.JSONObject:
        """Build a JSON object from this builder.

        Parameters
        ----------
        entity_factory : hikari.api.entity_factory.EntityFactory
            The entity factory to use to serialize entities within this builder.

        Returns
        -------
        hikari.internal.data_binding.JSONObject
            The built json object representation of this builder.
        """


class InteractionDeferredBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of a deferred message interaction response builder."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def type(self) -> base_interactions.DeferredResponseTypesT:
        """Return the type of this response.

        Returns
        -------
        hikari.interactions.bases.DeferredResponseTypesT
            The type of response this is.
        """

    @property
    @abc.abstractmethod
    def flags(self) -> typing.Union[undefined.UndefinedType, int, messages.MessageFlag]:
        """Message flags this response should have.

        !!! note
            As of writing the only message flag which can be set here is
            `hikari.messages.MessageFlag.EPHEMERAL`.

        Returns
        -------
        typing.Union[hikari.undefined.UndefinedType, builtins.int, hikari.messages.MessageFlag]
            The message flags this response should have if set else
            `hikari.undefined.UNDEFINED`.
        """

    @abc.abstractmethod
    def set_flags(self: _T, flags: typing.Union[undefined.UndefinedType, int, messages.MessageFlag], /) -> _T:
        """Set message flags for this response.

        !!! note
            As of writing, the only message flag which can be set is EPHEMERAL.

        Parameters
        ----------
        flags : typing.Union[hikari.undefined.UndefinedType, builtins.int, hikari.messages.MessageFlag]
            The message flags to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """


class InteractionMessageBuilder(InteractionResponseBuilder, abc.ABC):
    """Interface of an interaction message response builder used within REST servers.

    This can be returned by the listener registered to
    `hikari.api.interaction_server.InteractionServer` as a response to the interaction
    create.
    """

    __slots__: typing.Sequence[str] = ()

    # Required fields

    @property
    @abc.abstractmethod
    def type(self) -> base_interactions.MessageResponseTypesT:
        """Return the type of this response.

        Returns
        -------
        hikari.interactions.bases.MessageResponseTypesT
            The type of response this is.
        """

    # Extendable fields

    @property
    @abc.abstractmethod
    def embeds(self) -> typing.Sequence[embeds_.Embed]:
        """Sequence of up to 10 of the embeds included in this response.

        Returns
        -------
        typing.Sequence[hikari.embeds.Embed]
            A sequence of up to 10 ot the embeds included in this response.
        """

    # Settable fields

    @property
    @abc.abstractmethod
    def content(self) -> undefined.UndefinedOr[str]:
        """Response's message content.

        Returns
        -------
        hikari.undefined.UndefinedOr[builtins.str]
            The response's message content, if set.
        """

    @property
    @abc.abstractmethod
    def flags(self) -> typing.Union[undefined.UndefinedType, int, messages.MessageFlag]:
        """Message flags this response should have.

        !!! note
            As of writing the only message flag which can be set here is
            `hikari.messages.MessageFlag.EPHEMERAL`.

        Returns
        -------
        typing.Union[hikari.undefined.UndefinedType, builtins.int, hikari.messages.MessageFlag]
            The message flags this response should have if set else
            `hikari.undefined.UNDEFINED`.
        """

    @property
    @abc.abstractmethod
    def is_tts(self) -> undefined.UndefinedOr[bool]:
        """Whether this response's content should be treated as text-to-speech.

        Returns
        -------
        builtins.bool
            Whether this response's content should be treated as text-to-speech.
            If left as `hikari.undefined.UNDEFINED` then this will be disabled.
        """

    @property
    @abc.abstractmethod
    def mentions_everyone(self) -> undefined.UndefinedOr[bool]:
        """Whether @everyone and @here mentions should be enabled for this response.

        Returns
        -------
        hikari.undefined.UndefinedOr[builtins.bool]
            Whether @everyone mentions should be enabled for this response.
            If left as `hikari.undefined.UNDEFINED` then they will be disabled.
        """

    @property
    @abc.abstractmethod
    def role_mentions(
        self,
    ) -> undefined.UndefinedOr[typing.Union[snowflakes.SnowflakeishSequence[guilds.PartialRole], bool]]:
        """Whether and what role mentions should be enabled for this response.

        Returns
        -------
        hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], builtins.bool]]
            Either a sequence of object/IDs of the roles mentions should be enabled for,
            `builtins.False` or `hikari.undefined.UNDEFINED` to disallow any role
            mentions or `True` to allow all role mentions.
        """  # noqa: E501 - Line too long

    @property
    @abc.abstractmethod
    def user_mentions(
        self,
    ) -> undefined.UndefinedOr[typing.Union[snowflakes.SnowflakeishSequence[users.PartialUser], bool]]:
        """Whether and what user mentions should be enabled for this response.

        Returns
        -------
        hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], builtins.bool]]
            Either a sequence of object/IDs of the users mentions should be enabled for,
            `builtins.False` or `hikari.undefined.UNDEFINED` to disallow any user
            mentions or `True` to allow all user mentions.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def add_embed(self: _T, embed: embeds_.Embed, /) -> _T:
        """Add an embed to this response.

        Parameters
        ----------
        embed : hikari.embeds.Embed
            Object of the embed to add to this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def set_content(self: _T, content: undefined.UndefinedOr[str], /) -> _T:
        """Set the response's message content.

        Parameters
        ----------
        content : hikari.undefined.UndefinedOr[builtins.str]
            The message content to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def set_flags(self: _T, flags: typing.Union[undefined.UndefinedType, int, messages.MessageFlag], /) -> _T:
        """Set message flags for this response.

        !!! note
            As of writing, the only message flag which can be set is EPHEMERAL.

        Parameters
        ----------
        flags : typing.Union[hikari.undefined.UndefinedType, builtins.int, hikari.messages.MessageFlag]
            The message flags to set for this response.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def set_tts(self: _T, tts: undefined.UndefinedOr[bool], /) -> _T:
        """Set whether this response should trigger text-to-speech processing.

        Parameters
        ----------
        tts : Whether this response should trigger text-to-speech processing.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def set_mentions_everyone(self: _T, mentions: undefined.UndefinedOr[bool] = undefined.UNDEFINED, /) -> _T:
        """Set whether this response should be able to mention @everyone/@here.

        Parameters
        ----------
        mentions : hikari.undefined.UndefinedOr[builtins.bool]
            Whether this response should be able to mention @everyone/@here.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """

    @abc.abstractmethod
    def set_role_mentions(
        self: _T,
        mentions: undefined.UndefinedOr[
            typing.Union[snowflakes.SnowflakeishSequence[guilds.PartialRole], bool]
        ] = undefined.UNDEFINED,
        /,
    ) -> _T:
        """Set whether and what role mentions should be possible for this response.

        Parameters
        ----------
        mentions : hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], builtins.bool]]
            Either a sequence of object/IDs of the roles mentions should be enabled for,
            `builtins.False` or `hikari.undefined.UNDEFINED` to disallow any role
            mentions or `True` to allow all role mentions.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """  # noqa: E501 - Line too long

    @abc.abstractmethod
    def set_user_mentions(
        self: _T,
        mentions: undefined.UndefinedOr[
            typing.Union[snowflakes.SnowflakeishSequence[users.PartialUser], bool]
        ] = undefined.UNDEFINED,
        /,
    ) -> _T:
        """Set whether and what user mentions should be possible for this response.

        Parameters
        ----------
        mentions: hikari.undefined.UndefinedOr[typing.Union[hikari.snowflakes.SnowflakeishSequence[hikari.users.PartialUser], builtins.bool]]
            Either a sequence of object/IDs of the users mentions should be enabled for,
            `builtins.False` or `hikari.undefined.UNDEFINED` to disallow any user
            mentions or `True` to allow all user mentions.

        Returns
        -------
        InteractionMessageBuilder
            Object of this builder.
        """  # noqa: E501 - Line too long


class CommandBuilder(abc.ABC):
    """Interface of a command builder used when bulk creating commands over REST."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        r"""Name to set for this command.

        !!! warning
            This should match the regex `^[a-z0-9_-]{1,32}$`.

        Returns
        -------
        builtins.str
            The name to set for this command.
        """

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Return the description to set for this command.

        !!! warning
            This should be inclusively between 1-100 characters in length.

        Returns
        -------
        builtins.str
            The description to set for this command.
        """

    @property
    @abc.abstractmethod
    def options(self) -> typing.Sequence[commands.CommandOption]:
        """Sequence of up to 25 of the options set for this command.

        Returns
        -------
        typing.Sequence[hikari.interactions.commands.CommandOption]
            A sequence of up to 25 of the options set for this command.
        """

    @property
    @abc.abstractmethod
    def id(self) -> undefined.UndefinedOr[snowflakes.Snowflake]:
        """ID of this command.

        Returns
        -------
        hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID of this command if set.
        """

    @abc.abstractmethod
    def set_id(self: _T, id_: undefined.UndefinedOr[snowflakes.Snowflakeish], /) -> _T:
        """Set the ID of this command.

        Parameters
        ----------
        id_ : hikari.undefined.UndefinedOr[hikari.snowflakes.Snowflake]
            The ID to set for this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder.
        """

    @abc.abstractmethod
    def add_option(self: _T, option: commands.CommandOption) -> _T:
        """Add an option to this command.

        !!! note
            A command can have up to 25 options.

        Parameters
        ----------
        option : hikari.interactions.commands.CommandOption
            The option to add to this command.

        Returns
        -------
        CommandBuilder
            Object of this command builder.
        """

    @abc.abstractmethod
    def build(self, entity_factory: entity_factory_.EntityFactory, /) -> data_binding.JSONObject:
        """Build a JSON object from this builder.

        Parameters
        ----------
        entity_factory : hikari.api.entity_factory.EntityFactory
            The entity factory to use to serialize entities within this builder.

        Returns
        -------
        hikari.internal.data_binding.JSONObject
            The built json object representation of this builder.
        """
